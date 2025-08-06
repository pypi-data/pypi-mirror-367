from ambt.utils.runtime import detect_architecture 
from urllib.request import urlretrieve
from argparse import Namespace
from os import getcwd
import unix_ar
import tarfile
import subprocess

def binary_patcher(args: Namespace):
    libc: str = args.libc
    version: str = args.libc_version

    if not libc and not version:
        raise Exception("[AmbtPatcher] No libc binary/version string provided")

    if not version:
        strings_result = subprocess.run(["strings", self.libc], capture_output=True, text=True)
        for line in strings_result.stdout.splitlines():
            if "GNU C Library" in line:
                version = line

    if "ubuntu" in version or "debian" in version:
        _ = DebBinaryPatcher(libc, version)
    else:
        _ = GenericBinaryPatcher(libc, version)


class DebBinaryPatcher():
    
    def __init__(self, libc: str, version: str):
        self.libc: str = libc
        self.version: str = self.parse_version(version) if not libc else version
        self.arch: str = detect_architecture(libc) if libc else "amd64" 
        self.cwd: str = getcwd()

        package = self.fetch_package("libc6")
        self.find_library(package, "ld")

    def fetch_package(self, name: str):
        if "ubuntu" in self.version:
            url = f"https://launchpad.net/ubuntu/+archive/primary/+files/{name}_{self.version}_{self.arch}.deb"
        else:
            url = f"http://ftp.us.debian.org/debian/pool/main/g/glibc/{name}_{self.version}_{self.arch}.deb"

        file, _ = urlretrieve(url)
        return file

    def find_library(self, package: str, library: str):
        package_f: unix_ar.ArFile = unix_ar.open(package)
        package_files: list[unix_ar.ArInfo] = package_f.infolist()
        
        tarball = None
        for file in package_files:
            if b"data.tar" in file.name:
                tarball = package_f.open(file.name)
                break

        if not tarball:
            raise Exception("[AmbtPatcher] Unknown package format")

        tar_f = tarfile.open(fileobj=tarball) 
        path = None
        for member in tar_f.getmembers():
            if library in member.name:
                path = member.name
                tar_f.extract(member, self.cwd)
                break

        if not path:
            raise Exception("[AmbtPatcher] Unable to find target library")

    def parse_version(self, version: str):
        return version.split()[5][:-1]
