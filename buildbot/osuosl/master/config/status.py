from buildbot.process.properties import Interpolate
from buildbot.plugins import reporters

import config
#from zorg.buildbot.util.InformativeMailNotifier import InformativeMailNotifier

# Returns a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

def getReporters():

#    default_email = config.options.get('Master Options', 'default_email')

    return [

        # Note: reporters.GitHubStatusPush requires txrequests package to allow
        # interaction with GitHub REST API.
        reporters.GitHubStatusPush(
            str(config.options.get('GitHub Status', 'token')),
            context = Interpolate("%(prop:buildername)s"),
            verbose = True, # TODO: Turn off the verbosity once this is working reliably.
            builders = [
                "llvm-clang-x86_64-expensive-checks-ubuntu",
                "llvm-clang-x86_64-win-fast",
                "clang-x86_64-debian-fast",
                "llvm-clang-x86_64-expensive-checks-debian",
            ]),

        ]
