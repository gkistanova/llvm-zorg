from buildbot.process.properties import Interpolate
from buildbot.plugins import reporters

import config
from zorg.buildbot.util.InformativeMailNotifier import LLVMInformativeMailNotifier

# Returns a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

def getReporters():

    # Should be a single e-mail address
    status_email = str(config.options.get('Master Options', 'status_email')).split(',')

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

        reporters.IRC(
            useColors=False,
            host = str(config.options.get('IRC', 'host')),
            nick = str(config.options.get('IRC', 'nick')),
            channels = str(config.options.get('IRC', 'channels')).split(','),
            #authz=... # TODO: Consider allowing "harmful" operations to authorizes users.
            useRevisions = False, # FIXME: There is a bug in the buildbot
            showBlameList = True,
            notify_events = str(config.options.get('IRC', 'notify_events')).split(','),
            ),

        reporters.MailNotifier(
            mode = ('problem',),
            fromaddr = "llvm.buildmaster@lab.llvm.org", # TODO: Change this to buildmaster@lab.llvm.org.
            extraRecipients = status_email,
            extraHeaders = {"Reply-To": status_email[0]}, # The first from the list.
            lookup = "lab.llvm.org",
            messageFormatter = LLVMInformativeMailNotifier,
            # TODO: For debug purposes only. Remove later.
            dumpMailsToLog = True,
            ),

    ]
