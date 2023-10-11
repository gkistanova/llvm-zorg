from buildbot.plugins import steps, util

from zorg.buildbot.process.factory import LLVMBuildFactory
from zorg.buildbot.commands.LitTestCommand import LitTestCommand

# This builder is uses UnifiedTreeBuilders and adds running
# llvm-test-suite with cmake and ninja step.

def getTestSuiteSteps(
        compiler_dir,
        lit_args = [],
        env = None,
    ):

    test_suite_base_dir = util.Interpolate('%(prop:builddir)s/test')
    test_suite_src_dir = util.Interpolate('%(prop:builddir)s/test/test-suite')
    test_suite_workdir = util.Interpolate('%(prop:builddir)s/test/build-test-suite')

    env = env or {}

    f = LLVMBuildFactory(
            obj_dir             = "test/build-test-suite",
        )

    f.addStep(
        steps.RemoveDirectory(
            name            = 'Clean Test Suite Build dir',
            dir             = util.Interpolate(test_suite_workdir),
            description     = ["Removing the Test Suite build directory"],
            haltOnFailure   = True,
        ))

    f.addGetSourcecodeForProject(
            project         = 'test-suite',
            src_dir         = test_suite_src_dir,
            alwaysUseLatest = True
        )

    # Build a lit test command.
    lit_test_command = [util.Interpolate("%(kw:cc_dir)s/bin/llvm-lit", cc_dir=compiler_dir)]
    lit_test_command.extend(lit_args)
    lit_test_command.append(".")

    f.addSteps([
        steps.CMake(
            name            = 'cmake Test Suite',
            path            = test_suite_src_dir,
            generator       = 'Ninja',
            definitions     = {
                "CMAKE_C_COMPILER"          : util.Interpolate("%(kw:cc_dir)s/bin/clang", cc_dir=compiler_dir),
                "CMAKE_CXX_COMPILER"        : util.Interpolate("%(kw:cc_dir)s/bin/clang++", cc_dir=compiler_dir),
                "TEST_SUITE_LIT:FILEPATH"   : util.Interpolate("%(kw:cc_dir)s/bin/llvm-lit", cc_dir=compiler_dir),
            },
            description     = ['Running cmake on Test Suite dir'],
            haltOnFailure   = True,
            env             = env,
            workdir         = test_suite_workdir
        ),
        steps.CMake(
            name            = 'build Test Suite',
            options         = ["--build", "."],
            description     = ['Running Ninja on Test Suite dir'],
            haltOnFailure   = True,
            env             = env,
            workdir         = test_suite_workdir
        ),
        LitTestCommand(
            name            = 'Run Test Suite with lit',
            command         = lit_test_command,
            haltOnFailure   = True,
            description     = ['Running test suite tests'],
            env             = env,
            workdir         = test_suite_workdir,
        ),
    ])

    return f
