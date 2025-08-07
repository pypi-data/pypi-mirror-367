# g4hunter_parser.py

import argparse
from dna_ibp.help import Help

class G4HunterParser:
    def __init__(self, subparsers):
        self.g4hunter = subparsers.add_parser("g4hunter", help=Help.G4HUNTER.G4HUNTER)
        self.g4hunter_sub = self.g4hunter.add_subparsers(dest="subcommand")

        self._analyse_parser()
        self._show_parser()
        self._delete_parser()
        self._export_parser()

    def _analyse_parser(self):
        self.g4hunter_analyse = self.g4hunter_sub.add_parser("analyse", help=Help.G4HUNTER.ANALYSE)
        self.g4hunter_analyse.add_argument("sequence", help=Help.G4HUNTER.SEQUENCE)
        self.g4hunter_analyse.add_argument("--tags", nargs="*", help=Help.G4HUNTER.TAGS)
        self.g4hunter_analyse.add_argument("--threshold", "-t", type=float, default=1.2, help=Help.G4HUNTER.THRESHOLD)
        self.g4hunter_analyse.add_argument("--windowsize", "-w", type=int, default=25, help=Help.G4HUNTER.WINDOW_SIZE)

    def _show_parser(self):
        self.g4hunter_load = self.g4hunter_sub.add_parser("show", help=Help.G4HUNTER.SHOW)
        self.g4hunter_load.add_argument("result", help=Help.G4HUNTER.RESULT)
        self.g4hunter_load.add_argument("--details", "-d", action="store_true", help=Help.G4HUNTER.DETAILS)

    def _delete_parser(self):
        self.g4hunter_delete = self.g4hunter_sub.add_parser("delete", help=Help.G4HUNTER.DELETE)
        self.g4hunter_delete.add_argument("result", help=Help.G4HUNTER.SEQUENCE)

    def _export_parser(self):
        self.g4hunter_export = self.g4hunter_sub.add_parser("export", help=Help.G4HUNTER.EXPORT)
        self.g4hunter_export.add_argument("result", help=Help.G4HUNTER.RESULT)
        self.g4hunter_export.add_argument("--path", "-p", default="./", help=Help.G4HUNTER.PATH)
        self.g4hunter_export.add_argument("--aggregate", "-a", action=argparse.BooleanOptionalAction, default=True, help=Help.G4HUNTER.AGGREGATE)