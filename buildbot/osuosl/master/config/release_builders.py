from importlib import reload

from buildbot.plugins import util

from zorg.buildbot.builders import ClangBuilder
from zorg.buildbot.builders import FlangBuilder
from zorg.buildbot.builders import PollyBuilder
from zorg.buildbot.builders import LLDBBuilder
from zorg.buildbot.builders import SanitizerBuilder
from zorg.buildbot.builders import OpenMPBuilder
from zorg.buildbot.builders import SphinxDocsBuilder
from zorg.buildbot.builders import ABITestsuitBuilder
from zorg.buildbot.builders import ClangLTOBuilder
from zorg.buildbot.builders import UnifiedTreeBuilder
from zorg.buildbot.builders import AOSPBuilder
from zorg.buildbot.builders import AnnotatedBuilder
from zorg.buildbot.builders import LLDPerformanceTestsuite
from zorg.buildbot.builders import FuchsiaBuilder
from zorg.buildbot.builders import XToolchainBuilder


# Release builders.

all = [

# Clang builders.

    {'name' : "llvm-clang-x86_64-win-release",
    'tags'  : ["clang"],
    'workernames' : ["as-builder-3"],
    'builddir': "llvm-clang-x86_64-win-rel",
    'factory' : UnifiedTreeBuilder.getCmakeExBuildFactory(
                    vs="autodetect",
                    depends_on_projects=['llvm', 'clang'],
                    clean=True,
                    checks=[
                        "check-llvm-unit",
                        "check-clang-unit"
                    ],
                    cmake_definitions={
                        "LLVM_ENABLE_WERROR"            : "OFF",
                        "LLVM_TARGETS_TO_BUILD"         : "ARM",
                        "LLVM_DEFAULT_TARGET_TRIPLE"    : "armv7-unknown-linux-eabihf",
                        "LLVM_ENABLE_ASSERTIONS"        : "OFF",
                        "LLVM_OPTIMIZED_TABLEGEN"       : "OFF",
                        "LLVM_LIT_ARGS"                 : "-v --threads=32",
                    },
                )},

# Expensive checks builders.


    {'name' : "llvm-clang-x86_64-expensive-checks-ubuntu-release",
    'tags'  : ["llvm", "expensive-checks"],
    'workernames' : ["as-builder-4"],
    'builddir': "llvm-clang-x86_64-expensive-checks-ubuntu-rel",
    'factory' : UnifiedTreeBuilder.getCmakeExBuildFactory(
                    depends_on_projects=["llvm", "lld"],
                    clean=True,
                    cmake_definitions={
                        "LLVM_ENABLE_EXPENSIVE_CHECKS"  : "ON",
                        "LLVM_ENABLE_WERROR"            : "OFF",
                        "LLVM_USE_SPLIT_DWARF"          : "ON",
                        "LLVM_USE_LINKER"               : "gold",
                        "CMAKE_BUILD_TYPE"              : "Debug",
                        "CMAKE_CXX_FLAGS"               : "-U_GLIBCXX_DEBUG -Wno-misleading-indentation",
                        "LLVM_LIT_ARGS"                 : "-vv -j32",
                    },
                )},

    {'name' : "llvm-clang-x86_64-expensive-checks-win-release",
    'tags'  : ["llvm", "expensive-checks"],
    'workernames' : ["as-worker-93"],
    'builddir': "llvm-clang-x86_64-expensive-checks-win-rel",
    'factory' : UnifiedTreeBuilder.getCmakeExBuildFactory(
                    vs="autodetect",
                    depends_on_projects=["llvm", "lld"],
                    clean=True,
                    cmake_definitions={
                        "LLVM_ENABLE_EXPENSIVE_CHECKS"  : "ON",
                        "LLVM_ENABLE_WERROR"            : "OFF",
                        "CMAKE_BUILD_TYPE"              : "Debug",
                    },
                )},

    {'name' : "llvm-clang-x86_64-expensive-checks-debian-release",
    'tags'  : ["llvm", "expensive-checks"],
    'workernames' : ["gribozavr4"],
    'builddir': "llvm-clang-x86_64-expensive-checks-debian-rel",
    'factory' : UnifiedTreeBuilder.getCmakeExBuildFactory(
                    depends_on_projects=["llvm", "lld"],
                    clean=True,
                    cmake_definitions={
                        "LLVM_CCACHE_BUILD"             : "ON",
                        "LLVM_ENABLE_EXPENSIVE_CHECKS"  : "ON",
                        "LLVM_ENABLE_WERROR"            : "OFF",
                        "CMAKE_BUILD_TYPE"              : "Release",    #TODO:VV: why not Debug as all others?
                        "CMAKE_CXX_FLAGS"               : "-U_GLIBCXX_DEBUG",
                        "LLVM_LIT_ARGS"                 : "-v -vv -j96",
                    },
                    env={
                        'PATH':'/home/llvmbb/bin/clang-latest/bin:/home/llvmbb/bin:/usr/local/bin:/usr/local/bin:/usr/bin:/bin',
                        'CC': 'clang', 'CXX': 'clang++',
                    }
                )},

# Cross builders.

    {'name' : "llvm-clang-win-x-armv7l-release",
    'tags'  : ["clang", "llvm", "compiler-rt", "cross", "armv7"],
    'workernames' : ["as-builder-5"],
    'builddir': "x-armv7l-rel",
    'factory' : UnifiedTreeBuilder.getCmakeExBuildFactory(
                    depends_on_projects=[
                        "llvm",
                        "compiler-rt",
                        "clang",
                        "clang-tools-extra",
                        "libunwind",
                        "libcxx",
                        "libcxxabi",
                        "lld",
                    ],
                    # Suppress passing LLVM_ENABLE_RUNTIMES to CMake.
                    # We get this list from the CMake cache file.
                    enable_runtimes=None,
                    cmake_definitions={
                        "CMAKE_CXX_FLAGS"               : "-D__OPTIMIZE__",

                        "LLVM_TARGETS_TO_BUILD"         : "ARM",
                        "TOOLCHAIN_TARGET_TRIPLE"       : "armv7-unknown-linux-gnueabihf",
                        "DEFAULT_SYSROOT"               : "C:/buildbot/.arm-ubuntu",
                        "ZLIB_ROOT"                     : "C:/buildbot/.zlib-win32",
                        "LLVM_LIT_ARGS"                 : "-v -vv --threads=32",
                        "REMOTE_TEST_HOST"              : util.Interpolate("%(prop:remote_test_host:-)s"),
                        "REMOTE_TEST_USER"              : util.Interpolate("%(prop:remote_test_user:-)s"),
                    },
                    cmake_options=[
                        "-C", util.Interpolate("%(prop:srcdir_relative)s/clang/cmake/caches/CrossWinToARMLinux.cmake")
                    ],
                    allow_cmake_defaults=True,
                    checks=[
                        "check-llvm",
                        "check-clang",
                        "check-lld",
                        "check-compiler-rt-armv7-unknown-linux-gnueabihf"
                    ],
                    checks_on_target=[
                        ("libunwind",
                            ["python", "bin/llvm-lit.py",
                            "-v", "-vv", "--threads=32",
                            "runtimes/runtimes-armv7-unknown-linux-gnueabihf-bins/libunwind/test"]),
                        ("libc++abi",
                            ["python", "bin/llvm-lit.py",
                            "-v", "-vv", "--threads=32",
                            "runtimes/runtimes-armv7-unknown-linux-gnueabihf-bins/libcxxabi/test"]),
                        ("libc++",
                            ['python', 'bin/llvm-lit.py',
                            '-v', '-vv', '--threads=32',
                            'runtimes/runtimes-armv7-unknown-linux-gnueabihf-bins/libcxx/test',
                            ])
                    ],
                    vs="autodetect",
                    install_dir="install",
                    clean=True,
                    env = {
                        # TMP/TEMP within the build dir (to utilize a ramdisk).
                        'TMP'        : util.Interpolate("%(prop:builddir)s/%(prop:objdir)s"),
                        'TEMP'       : util.Interpolate("%(prop:builddir)s/%(prop:objdir)s"),
                    }
                )},

    {'name' : "llvm-clang-win-x-aarch64-release",
    'tags'  : ["clang", "llvm", "compiler-rt", "cross", "aarch64"],
    'workernames' : ["as-builder-6"],
    'builddir': "x-aarch64-rel",
    'factory' : UnifiedTreeBuilder.getCmakeExBuildFactory(
                    depends_on_projects=[
                        "llvm",
                        "compiler-rt",
                        "clang",
                        "clang-tools-extra",
                        "libunwind",
                        "libcxx",
                        "libcxxabi",
                        "lld",
                    ],
                    # Suppress passing LLVM_ENABLE_RUNTIMES to CMake.
                    # We get this list from the CMake cache file.
                    enable_runtimes=None,
                    cmake_definitions={
                        "CMAKE_CXX_FLAGS"               : "-D__OPTIMIZE__",

                        "LLVM_TARGETS_TO_BUILD"         : "AArch64",
                        "TOOLCHAIN_TARGET_TRIPLE"       : "aarch64-unknown-linux-gnu",
                        "DEFAULT_SYSROOT"               : "C:/buildbot/.aarch64-ubuntu",
                        "ZLIB_ROOT"                     : "C:/buildbot/.zlib-win32",
                        "LLVM_LIT_ARGS"                 : "-v -vv --threads=32",
                        "REMOTE_TEST_HOST"              : util.Interpolate("%(prop:remote_test_host:-)s"),
                        "REMOTE_TEST_USER"              : util.Interpolate("%(prop:remote_test_user:-)s"),
                    },
                    cmake_options=[
                        "-C", util.Interpolate("%(prop:srcdir_relative)s/clang/cmake/caches/CrossWinToARMLinux.cmake")
                    ],
                    allow_cmake_defaults=True,
                    checks=[
                        "check-llvm",
                        "check-clang",
                        "check-lld",
                        "check-compiler-rt-aarch64-unknown-linux-gnu"
                    ],
                    checks_on_target=[
                        ("libunwind",
                            ["python", "bin/llvm-lit.py",
                            "-v", "-vv", "--threads=32",
                            "runtimes/runtimes-aarch64-unknown-linux-gnu-bins/libunwind/test"]),
                        ("libc++abi",
                            ["python", "bin/llvm-lit.py",
                            "-v", "-vv", "--threads=32",
                            "runtimes/runtimes-aarch64-unknown-linux-gnu-bins/libcxxabi/test"]),
                        ("libc++",
                            ['python', 'bin/llvm-lit.py',
                            '-v', '-vv', '--threads=32',
                            'runtimes/runtimes-aarch64-unknown-linux-gnu-bins/libcxx/test',
                            ])
                    ],
                    vs="autodetect",
                    install_dir="install",
                    clean=True,
                    env = {
                        # TMP/TEMP within the build dir (to utilize a ramdisk).
                        'TMP'        : util.Interpolate("%(prop:builddir)s/%(prop:objdir)s"),
                        'TEMP'       : util.Interpolate("%(prop:builddir)s/%(prop:objdir)s"),
                    }
                )},

# LLD builders.

    {'name' : "lld-x86_64-win-release",
    'tags'  : ["lld"],
    'workernames' : ["as-worker-93"],
    'builddir': "lld-x86_64-win-rel",
    'factory' : UnifiedTreeBuilder.getCmakeExBuildFactory(
                    depends_on_projects=['llvm', 'lld'],
                    vs="autodetect",
                    cmake_definitions={
                        "LLVM_ENABLE_WERROR"            : "OFF",
                    },
                )},

    {'name' : "lld-x86_64-ubuntu-release",
    'tags'  : ["lld"],
    'workernames' : ["as-builder-4"],
    'builddir' : "lld-x86_64-ubuntu-rel",
    'factory': UnifiedTreeBuilder.getCmakeExBuildFactory(
                    depends_on_projects=['llvm', 'lld'],
                    clean=True,
                    cmake_definitions={
                        "LLVM_ENABLE_WERROR"            : "OFF",
                    },
                )},

# LTO and ThinLTO builders.

    {'name' : "clang-with-thin-lto-ubuntu-release",
    'tags'  : ["clang", "lld", "LTO"],
    'workernames' : ["as-worker-92"],
    'builddir': "clang-with-thin-lto-ubuntu-rel",
    'factory' : ClangLTOBuilder.getClangWithLTOBuildFactory(jobs=72, lto='thin')},

    {'name' : "clang-with-lto-ubuntu-release",
    'tags'  : ["clang", "lld", "LTO"],
    'workernames' : ["as-worker-91"],
    'builddir': "clang-with-lto-ubuntu-rel",
    'factory' : ClangLTOBuilder.getClangWithLTOBuildFactory(
                    jobs=72,
                    extra_configure_args_lto_stage=[
                        '-DLLVM_PARALLEL_LINK_JOBS=14',
                    ])},

# OpenMP builders.

    {'name' : "openmp-clang-x86_64-linux-debian-release",
    'tags'  : ["openmp"],
    'workernames' : ["gribozavr4"],
    'builddir': "openmp-clang-x86_64-linux-debian-rel",
    'factory' : OpenMPBuilder.getOpenMPCMakeBuildFactory(
                    extraCmakeArgs=[
                        '-DLLVM_CCACHE_BUILD=ON',
                    ],
                    env={
                        'PATH':'/home/llvmbb/bin/clang-latest/bin:/home/llvmbb/bin:/usr/local/bin:/usr/local/bin:/usr/bin:/bin',
                        'CC': 'clang', 'CXX': 'clang++',
                    })},

# Sony builders.

    {'name' : "llvm-clang-x86_64-sie-win-release",
    'tags'  : ["llvm", "clang", "clang-tools-extra", "lld", "cross-project-tests"],
    'workernames' : ["sie-win-worker"],
    'builddir': "x86_64-sie-win-rel",
    'factory' : UnifiedTreeBuilder.getCmakeExBuildFactory(
                    vs="autodetect",
                    vs_arch='x64',
                    depends_on_projects=['llvm', 'clang', 'clang-tools-extra', 'lld', 'cross-project-tests'],
                    clean=True,
                    cmake_definitions={
                        "CMAKE_BUILD_TYPE"              : "Release",
                        "CLANG_ENABLE_ARCMT"            : "OFF",
                        "CLANG_ENABLE_CLANGD"           : "OFF",
                        "LLVM_CCACHE_BUILD"             : "ON",
                        "LLVM_DEFAULT_TARGET_TRIPLE"    : "x86_64-sie-ps5",
                        "LLVM_INCLUDE_EXAMPLES"         : "OFF",
                        "LLVM_TARGETS_TO_BUILD"         : "X86",
                        "LLVM_VERSION_SUFFIX"           : "",       #TODO:VV: is this def should be empty?
                        "LLVM_BUILD_RUNTIME"            : "OFF",
                        "LLVM_ENABLE_ASSERTIONS"        : "ON",
                        "LLVM_LIT_ARGS"                 : "--verbose",
                    }
                )},

    {'name': "llvm-clang-x86_64-gcc-ubuntu-release",
    'tags'  : ["llvm", "clang", "clang-tools-extra", "compiler-rt", "lld", "cross-project-tests"],
    'workernames': ["doug-worker-2a"],
    'builddir': "x86_64-gcc-rel",
    'factory': UnifiedTreeBuilder.getCmakeExBuildFactory(
                    depends_on_projects=['llvm', 'clang', 'clang-tools-extra', 'compiler-rt', 'lld', 'cross-project-tests'],
                    cmake_definitions={
                        "CMAKE_C_COMPILER"              : "gcc",
                        "CMAKE_CXX_COMPILER"            : "g++",
                        "CMAKE_BUILD_TYPE"              : "Release",
                        "CLANG_ENABLE_CLANGD"           : "OFF",
                        "LLVM_BUILD_RUNTIME"            : "ON",
                        "LLVM_BUILD_TESTS"              : "ON",
                        "LLVM_ENABLE_ASSERTIONS"        : "ON",
                        "LLVM_INCLUDE_EXAMPLES"         : "OFF",
                        "LLVM_LIT_ARGS"                 : "--verbose -j48",
                        "LLVM_PARALLEL_LINK_JOBS"       : "16",
                        "LLVM_USE_LINKER"               : "gold",
                    }
                )},

]
