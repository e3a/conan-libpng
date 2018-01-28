from conans import ConanFile, tools
from conans.tools import download, untargz
import os

class PopplerConan(ConanFile):
    name = "libpng"
    version = "1.6.34"
    license = "libpng license"
    url = "http://www.libpng.org/pub/png/libpng.html"
    description = "libpng is the official PNG reference library."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "txt"
    requires = "zlib/1.2.11@conan/stable"

    def run_bash(self, cmd):
        if self.settings.os == "Windows":
            tools.run_in_windows_bash(self, cmd)
        else:
            self.run(cmd)

    def source(self):
        tarball_name = 'libpng.tar.gz'
        download("http://prdownloads.sourceforge.net/libpng/libpng-%s.tar.gz?download" % (self.version), tarball_name)
        untargz(tarball_name)
        os.unlink(tarball_name)

    def build(self):
        zlib_info = self.deps_cpp_info["zlib"]
        zlib_library = zlib_info.lib_paths[0]
        zlib_include = zlib_info.include_paths[0]

        with tools.chdir("libpng-%s" % self.version) :
            configure_cmd = "export ZLIBLIB=%s && export ZLIBINC=%s &&  LD_LIBRARY_PATH=\"$ZLIBLIB:$LD_LIBRARY_PATH\" export LD_LIBRARY_PATH && CPPFLAGS=\"-I$ZLIBINC\" export CPPFLAGS LDFLAGS=\"-L$ZLIBLIB\" export LDFLAGS && ./configure " % (zlib_library, zlib_include)
            if not self.options.shared:
                configure_cmd += " --disable-shared "
            if self.settings.os=="Windows":
                configure_cmd += " --toolchain=msvc"
            self.run_bash(configure_cmd)
            self.run_bash("make")

    def package(self):
        self.copy("*.h", dst="include", src=".", keep_path=True)
        if self.options.shared:
            if self.settings.os == "Macos":
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.so*", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["png"]

