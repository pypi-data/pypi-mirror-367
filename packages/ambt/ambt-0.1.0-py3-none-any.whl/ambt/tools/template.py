from ambt.utils.typing import bytes_to_str
from ambt.utils.runtime import detect_environment, AmbtEnv
from urllib.request import urlopen
from argparse import Namespace
from os.path import abspath, normpath 
import re

def template_generator(args: Namespace):
    env: str = detect_environment(args.binary) 

    if env == AmbtEnv.USERSPACE:
        _ = PwntoolsTemplateGenerator(args)
    
    elif env == AmbtEnv.KERNEL:
        raise Exception("TODO")

    elif env == AmbtEnv.BROWSER:
        raise Exception("TODO")

    else:
        raise Exception("[AmbtTemplate] Unknown environment type")


class TemplateGenerator():

    uri: str = ""
    template: str = ""

    def fetch_template(self):
        try:
            self.template = bytes_to_str(urlopen(self.uri).read()) 
        except:
            raise Exception("[AmbtTemplate] Unable to fetch template")

    def default_template_path(self, template: str):
        return "file://" + normpath(abspath(__file__) + f"/../../resources/template/{template}")

    def parse_remote(self, remote: str) -> tuple[str, str]:
        if not remote:
            return ("", "")

        remote_tokens = remote.split()
        if len(remote_tokens) == 3:
            return (remote_tokens[1], remote_tokens[2])
        if len(remote_tokens) == 2:
            _ = remote_tokens.pop(0)
        if len(remote_tokens) == 1:
            remote_tokens = remote_tokens[0].split(":")
            return (remote_tokens[0], remote_tokens[1])
        else:
            raise Exception("[AmbtTemplate] Invalid remote format")


class PwntoolsTemplateGenerator(TemplateGenerator):

    def __init__(self, args: Namespace):
        self.uri = args.uri if args.uri else self.default_template_path("pwntools") 
        self.binary: str = args.binary
        self.libc: str = args.libc
        self.remote: tuple[str, str] = self.parse_remote(args.remote)

        self.fetch_template()
        self.parse_template()
        self.write_template()
        print("[*] Generated template!", end="")

    def parse_template(self):
        libc_pattern: str = r'<libc>(.*?)</libc>'
        remote_pattern: str = r'<remote>(.*?)</remote>'

        self.template = self.template.replace('<BINARY>', self.binary)

        if self.libc:
            libc_blocks: list[str] = re.findall(libc_pattern, self.template, re.DOTALL)
            for block in libc_blocks:
                replacement = block.replace('<LIBC>', self.libc)
                self.template = self.template.replace(f"<libc>{block}</libc>", replacement)
        else:
            self.template = re.sub(libc_pattern, '', self.template, flags=re.DOTALL)

        if self.remote[0]:
            host, port = self.remote

            remote_blocks: list[str] = re.findall(remote_pattern, self.template, re.DOTALL)
            for block in remote_blocks:
                replacement = block.replace('<HOST>', host)
                replacement = replacement.replace('<PORT>', port)
                self.template = self.template.replace(f"<remote>{block}</remote>", replacement)
        else:
            self.template = re.sub(remote_pattern, '', self.template, flags=re.DOTALL)


    def write_template(self):
        file_name = input("Enter exploit file name (exp.py): ")

        if not file_name or file_name.lower() == 'y':
            file_name = "exp.py"

        _ = open(file_name, "w+").write(self.template) 
