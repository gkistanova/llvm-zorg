from twisted.internet import defer

@defer.inlineCallbacks
def collapseRequests(master, builder, req1, req2):
    """
    Returns true if both buildrequest can be merged, via Deferred.

    This function is called from addBuildset(), so buildset is always the same.
    Note req2 will be collapsed if returned True.

    This implements Zorg's default collapse strategy.
    """

    # Do not collapse if builders are different.
    if req1['builderid'] != req2['builderid']:
        return False

    # Check properties and do not collapse if properties do not match.
    if req1.get('properties', None) != req2.get('properties', None):
        return False

    # Build requests with different reasons should be built separately.
    if req1.get('reason', None) != req2.get('reason', None):
        return False

    return True
