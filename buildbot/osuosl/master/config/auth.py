#from buildbot.www.auth import NoAuth
from buildbot.plugins import util

#from twisted.python import log

def getAuth():
    # For test local setup use NoAuth instead.
    auth = util.GitHubAuth(
        clientId=str("<put clientId here"), # TODO: Move this to local.cfg.
        clientSecret=str("<put clientSecret here>"), # TODO: Move this to local.cfg.
        apiVersion=4,
        getTeamsMembership=True,
        #debug=True, # TODO: Turn this to false once validated working.
    )
    return auth


def getAuthz():

    authz = util.Authz(
        allowRules=[
            util.AnyEndpointMatcher(defaultDeny=False),

            # Admins can do anything.
            util.AnyEndpointMatcher(role="admins", defaultDeny=False),
            # Allow authors to stop, force or rebuild their own builds,
            # allow core devs to stop, force or rebuild any build.
            util.StopBuildEndpointMatcher(role="owner", defaultDeny=False),
            util.StopBuildEndpointMatcher(
                role="buildbot-owners", defaultDeny=False
            ),
            util.StopBuildEndpointMatcher(role="???"),
            util.RebuildBuildEndpointMatcher(role="owner", defaultDeny=False),
            util.RebuildBuildEndpointMatcher(
                role="buildbot-owners", defaultDeny=False
            ),
            util.RebuildBuildEndpointMatcher(role="???"),
            util.ForceBuildEndpointMatcher(role="owner", defaultDeny=False),
            util.ForceBuildEndpointMatcher(role="???"),
            # Future-proof control endpoints.
            util.AnyControlEndpointMatcher(role="admins"),
        ],
        roleMatchers=[
            util.RolesFromGroups(groupPrefix="llvm/"),
            util.RolesFromOwner(role="owner"),
            util.RolesFromUsername(
                roles=["admins"],
                usernames=[       # TODO: Move this to local.cfg.
                    "gkistanova",
                    "andreil99",
                ],
            ),
        ],
    )

    return authz
