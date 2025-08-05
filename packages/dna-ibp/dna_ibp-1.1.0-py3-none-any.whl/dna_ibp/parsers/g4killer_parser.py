# g4killer_parser.py

import argparse
from dna_ibp.help import Help

class G4KillerParser:
    def __init__(self, subparsers):
        self.g4killer = subparsers.add_parser("g4killer", help=Help.G4KILLER.G4KILLER)
        self.g4killer_sub = self.g4killer.add_subparsers(dest="subcommand")

        self._run_parser()

    def _run_parser(self):
        self.g4killer_run = self.g4killer_sub.add_parser("run", help=Help.G4KILLER.RUN)
        self.g4killer_run.add_argument("sequence", nargs="+", help=Help.G4KILLER.SEQUENCE)
        self.g4killer_run.add_argument("--complementary", action=argparse.BooleanOptionalAction, default=False, help=Help.G4KILLER.COMPLEMENTARY)
        self.g4killer_run.add_argument("--threshold", "-t", type=float, default=1.0, help=Help.G4KILLER.THRESHOLD)