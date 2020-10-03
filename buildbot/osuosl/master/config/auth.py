import config

#from buildbot.www.auth import NoAuth
from buildbot.plugins import util

#from twisted.python import log

def getAuth():
    # For test local setup use NoAuth instead.
    auth = util.GitHubAuth(
        clientId=str(config.options.get('GitHub Auth', 'clientId')),
        clientSecret=str(config.options.get('GitHub Auth', 'clientSecret')),
        apiVersion=4,
        getTeamsMembership=True,
        debug=True, # TODO: Turn this to false once validated working.
    )
    return auth


def getAuthz():

    authz = util.Authz(
        allowRules=[
            util.AnyEndpointMatcher(role="viewers", defaultDeny=False),

            # Admins can do anything.
            # defaultDeny=False: if user does not have the admin role,
            # we continue parsing rules.
            util.AnyEndpointMatcher(role="admins", defaultDeny=False),

            # Allow authors to stop, force or rebuild their own builds,
            util.StopBuildEndpointMatcher(role="owner", defaultDeny=False),
            # Allow bot owners to stop, force or rebuild on their own bots,
            util.StopBuildEndpointMatcher(role="worker-owner", defaultDeny=False),

            # allow core devs to force or rebuild any build.
            util.RebuildBuildEndpointMatcher(role="owner", defaultDeny=False),
            util.RebuildBuildEndpointMatcher(role="worker-owner", defaultDeny=False),
            util.RebuildBuildEndpointMatcher(role="developers"),

            util.ForceBuildEndpointMatcher(role="owner", defaultDeny=False),
            util.ForceBuildEndpointMatcher(role="worker-owner", defaultDeny=False),
            util.ForceBuildEndpointMatcher(role="developers"),

            # Future-proof control endpoints. No parsing rules beyond this.
            util.AnyControlEndpointMatcher(role="admins"),
        ],
        roleMatchers=[
            util.RolesFromGroups(groupPrefix="llvm/"),
            # role owner is granted when property owner matches the email of the user
            util.RolesFromOwner(role="owner"),
            util.RolesFromUsername(
                roles=["admins"],
                usernames=config.options.options("Admins"),
            ),
        ],
    )

    return authz
