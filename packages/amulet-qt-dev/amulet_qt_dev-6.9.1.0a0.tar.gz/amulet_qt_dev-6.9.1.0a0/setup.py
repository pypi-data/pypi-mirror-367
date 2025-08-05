import os
import sys
from pathlib import Path
import subprocess
import platform
from tempfile import TemporaryDirectory

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.bdist_wheel import bdist_wheel


class CMakeBuild(build_ext):
    def build_extension(self, ext):
        if self.editable_mode:
            raise RuntimeError("This library cannot be installed in editable mode")
        else:
            install_dir = (Path.cwd() / self.get_ext_fullpath("")).parent.resolve() / "qt_dev"

        os.makedirs(install_dir, exist_ok=True)

        platform_args = []
        platform_post_args = []
        if sys.platform == "win32":
            platform_args.extend(["-cmake-generator", "Visual Studio 17 2022"])
            if sys.maxsize > 2**32:
                platform_post_args.extend(["-A", "x64"])
            else:
                platform_post_args.extend(["-A", "Win32"])
            platform_post_args.extend(["-T", "v143"])
        elif sys.platform == "darwin":
            if platform.machine() == "arm64":
                platform_post_args.append("-DCMAKE_OSX_ARCHITECTURES=x86_64;arm64")

        if subprocess.run(["cmake", "--version"]).returncode:
            raise RuntimeError("Could not find cmake")

        with TemporaryDirectory(prefix="qt") as tempdir:
            src_dir = os.path.join(tempdir, "src")
            build_dir = os.path.join(tempdir, "build")
            os.makedirs(build_dir, exist_ok=True)
            if subprocess.run(["git", "clone", "--branch", "v6.9.1", "git://code.qt.io/qt/qt5.git", src_dir]).returncode:
                raise RuntimeError("Could not clone qt-src")
            if subprocess.run(
                [
                    os.path.join(src_dir, "configure.bat" if os.name == "nt" else "configure"),
                    "-release",
                    *platform_args,
                    "-init-submodules",
                    "-submodules",
                    "qtbase",
                    "--",
                    "-DQT_BUILD_EXAMPLES_BY_DEFAULT=OFF",
                    "-DQT_BUILD_TESTS_BY_DEFAULT=OFF",
                    "-DQT_BUILD_TOOLS_BY_DEFAULT=OFF",
                    *platform_post_args,
                ],
                cwd=build_dir,
            ).returncode:
                raise RuntimeError("Error configuring qt")
            if subprocess.run(
                ["cmake", "--build", build_dir, "--parallel", "--config", "Release"]
            ).returncode:
                raise RuntimeError("Error building qt")
            if subprocess.run(
                ["cmake", "--install", build_dir, "--config", "Release", "--prefix", install_dir]
            ).returncode:
                raise RuntimeError("Error installing qt")


class BDistWheel(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            return "py3", "none", plat

        return python, abi, plat


setup(
    cmdclass={
        "bdist_wheel": BDistWheel,
        "build_ext": CMakeBuild
    },
    ext_modules=[
        Extension("qt_dev", [])
    ]
)
