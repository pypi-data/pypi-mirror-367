# __init__.py

import argparse
from dna_ibp.parsers.sequence_parser import SequenceParser
from dna_ibp.parsers.g4hunter_parser import G4HunterParser
from dna_ibp.parsers.rloop_parser import RloopParser
from dna_ibp.parsers.zdna_parser import ZDnaParser
from dna_ibp.parsers.cpx_parser import CpXParser
from dna_ibp.parsers.g4killer_parser import G4KillerParser
from dna_ibp.parsers.p53_parser import P53Parser
from dna_ibp.__version__ import __version__

__all__ = ["Parsers"]

class Parsers:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="dna-ibp")
        self.parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {__version__}")
        self.parser.add_argument("--reset", "-r", action="store_true")
        self.subparsers = self.parser.add_subparsers(dest="command")

        self.sequence_parser: SequenceParser = SequenceParser(subparsers=self.subparsers)
        self.g4hunter_parser: G4HunterParser = G4HunterParser(subparsers=self.subparsers)
        self.rloop_parser: RloopParser = RloopParser(subparsers=self.subparsers)
        self.zdna_parser: ZDnaParser = ZDnaParser(subparsers=self.subparsers)
        self.cpx_parser: CpXParser = CpXParser(subparsers=self.subparsers)
        self.g4killer_parser: G4KillerParser = G4KillerParser(subparsers=self.subparsers)
        self.p53_parser: P53Parser = P53Parser(subparsers=self.subparsers)

    def parse_args(self, *args, **kwargs):
        return self.parser.parse_args(*args, **kwargs)

    def print_help(self):
        return self.parser.print_help() 

