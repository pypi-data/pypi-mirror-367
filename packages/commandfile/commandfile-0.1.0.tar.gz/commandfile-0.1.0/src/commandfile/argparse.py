import logging
import sys
from argparse import ArgumentParser, Namespace
from itertools import chain

import yaml

from commandfile.model import Commandfile

logger = logging.getLogger(__name__)


class CommandfileArgumentParser(ArgumentParser):
    def __init__(self, *, implicit_arg: str = "--commandfile", **kwargs):
        super().__init__(**kwargs)
        self.implicit_arg = implicit_arg
        self.implicit_dest = implicit_arg.lstrip(self.prefix_chars).replace("-", "_")

    def parse_args(self, args=None, namespace=None) -> Namespace:
        remaining_argv = self._parse_commandfile_arg(args)
        return super().parse_args(remaining_argv, namespace)

    def parse_known_args(
        self, args=None, namespace=None
    ) -> tuple[Namespace, list[str]]:
        remaining_argv = self._parse_commandfile_arg(args)
        return super().parse_known_args(remaining_argv, namespace)

    def _parse_commandfile_arg(self, args=None):
        if args is None:
            args = sys.argv[1:]

        # Create a minimal parser to find the implicit argument without
        # raising errors for other unknown arguments.
        pre_parser = ArgumentParser(add_help=False)
        pre_parser.add_argument(self.implicit_arg, type=str)
        pre_args, remaining_argv = pre_parser.parse_known_args(args)

        commandfile_path = getattr(pre_args, self.implicit_dest)
        if commandfile_path:
            commandfile = self._load_commandfile(commandfile_path)
            logger.debug("Loaded commandfile %s: %s", commandfile_path, commandfile)
            # Prepend commandfile args to the remaining command-line args.
            # This ensures that command-line args can override file-based args.
            remaining_argv = [*self._commandfile_to_argv(commandfile), *remaining_argv]
        return remaining_argv

    def _load_commandfile(self, path: str):
        """Load a Commandfile from a YAML file."""
        with open(path) as f:
            raw = yaml.safe_load(f)

        return Commandfile(**raw)

    def _commandfile_to_argv(self, commandfile: Commandfile) -> list[str]:
        """Convert a Commandfile to a list of command-line arguments."""
        argv = []
        for item in commandfile.parameters:
            argv.extend([f"--{item.key}", str(item.value)])

        for filelist in chain(commandfile.inputs, commandfile.outputs):
            argv.append(f"--{filelist.key}")
            argv.extend(map(str, filelist.files))

        return argv
