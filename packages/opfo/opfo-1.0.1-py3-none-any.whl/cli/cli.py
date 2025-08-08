from argparse import Namespace
import argparse
import sys

from .check import check_config
from util.get_logger import get_logger
from .organize_files import organize_files

class Cli:
    __version__ = '1.0.1'
    def setup(self) -> Namespace:
        parser = argparse.ArgumentParser(prog="opfo", description="opfo is an advanced file organizer implemented in python")
        parser.add_argument("-V", "--version", action="version",version=f"%(prog)s {self.__version__}")
        parser.add_argument("-c", "--check", action="store_true", help="check if the current config file is valid")
        parser.add_argument("-v", "--verbose", action="store_true", help="gives more insight on what is happening the organization of files happens")
        
        return parser.parse_args()


    def route_options(self, args: Namespace, config_file: str) -> None:
        logger = get_logger()
        if args.check:
            is_ok = check_config(config_file=config_file)
            if not is_ok:
                sys.exit(1)
            logger.info("All Good!")
            sys.exit(0)
        if args.verbose:
            organize_files(config_file=config_file, verbose=True)
            sys.exit(0)
        organize_files(config_file=config_file, verbose=False)