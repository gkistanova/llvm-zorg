from twisted.python import log
from twisted.internet import defer

@defer.inlineCallbacks
def collapseRequests(master, builder, req1, req2):
    #log.msg(">>> collapseRequests(master=%s,builder=%s,req1=%s,req2=%s)" % (master, builder.__dict__, req1, req2))

    """
    Returns true if both buildrequest can be merged, via Deferred.

    This implements Zorg's default collapse strategy.
    """
     # If these are for the same buildset, collapse away
    if req1['buildsetid'] == req2['buildsetid']:
        return True

    # Get the buidlsets for each buildrequest
    selfBuildsets = yield master.data.get(
        ('buildsets', str(req1['buildsetid'])))
    otherBuildsets = yield master.data.get(
        ('buildsets', str(req2['buildsetid'])))

    # extract sourcestamps, as dictionaries by codebase
    selfSources = dict((ss['codebase'], ss)
                        for ss in selfBuildsets['sourcestamps'])
    otherSources = dict((ss['codebase'], ss)
                        for ss in otherBuildsets['sourcestamps'])
    log.msg(">>> collapseRequests: sourcestamps self=%s and other=%s" % (selfSources, otherSources))

    # if the sets of codebases do not match, we can't collapse
    if set(selfSources) != set(otherSources):
        #log.msg("   >>> collapseRequests: Returns false, as codebases do not match.")
        return False

    for c, selfSS in selfSources.items():
        otherSS = otherSources[c]
        if selfSS['repository'] != otherSS['repository']:
            return False

        if selfSS['branch'] != otherSS['branch']:
            log.msg("   >>> collapseRequests: Returns false, as branches do not match.")
            return False

        # TODO: Handle projects matching if we ever would have
        # a mix of projects from the monorepo and outside of
        # the monorepo. For now, we consider all of them being
        # a part of the monorepo, so all of them are compatible
        # and could be collapsed.

        # anything with a patch won't be collapsed
        if selfSS['patch'] or otherSS['patch']:
            #log.msg("   >>> collapseRequests: Returns false, as there a patch.")
            return False

        # get changes & compare
        selfChanges = yield master.data.get(('sourcestamps', selfSS['ssid'], 'changes'))
        otherChanges = yield master.data.get(('sourcestamps', otherSS['ssid'], 'changes'))
        # if both have changes, proceed, else fail - if no changes check revision instead
        #log.msg("   >>> collapseRequests: selfChanges=%s, otherChanges=%s" % (selfChanges, otherChanges))
        if selfChanges and otherChanges:
            #log.msg("   >>> collapseRequests: selfChanges and otherChanges: continue.")
            continue

        if selfChanges and not otherChanges:
            #log.msg("   >>> collapseRequests: Returns false, as selfChanges and not otherChanges.")
            return False

        if not selfChanges and otherChanges:
            #log.msg("   >>> collapseRequests: Returns false, as not selfChanges and otherChanges.")
            return False

        # else check revisions
        if selfSS['revision'] != otherSS['revision']:
            #log.msg("   >>> collapseRequests: Returns false, as revisions do not match.")
            return False

    # Build requests with different reasons should be built separately.
    if req1.get('reason', None) == req2.get('reason', None):
        log.msg("   >>> collapseRequests: Can collapse requests %s and %s" % (req1, req2))
        return True
    else:
        log.msg("   >>> collapseRequests: Returns false, as reasons do not match for %s and %s" % (req1, req2))
        return False
