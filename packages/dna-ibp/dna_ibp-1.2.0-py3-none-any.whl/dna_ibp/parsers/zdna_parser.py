# zdna_parser.py

from dna_ibp.help import Help

class ZDnaParser:
    def __init__(self, subparsers):
        self.zdna = subparsers.add_parser("zdna", help=Help.ZDNA.ZDNA)
        self.zdna_sub = self.zdna.add_subparsers(dest="subcommand")

        self._analyse_parser()
        self._show_parser()
        self._delete_parser()
        self._export_parser()

    def _analyse_parser(self):
        self.zdna_analyse = self.zdna_sub.add_parser("analyse", help=Help.ZDNA.ANALYSE)
        self.zdna_analyse.add_argument("sequence", help=Help.ZDNA.SEQUENCE)
        self.zdna_analyse.add_argument("--mss", "--min-window-size", type=int, default=10, help=Help.ZDNA.MSS)
        self.zdna_analyse.add_argument("--model", type=str, default="1", help=Help.ZDNA.MODEL)
        self.zdna_analyse.add_argument("--gc", type=float, default=25, help=Help.ZDNA.GC)
        self.zdna_analyse.add_argument("--gtac", type=float, default=3, help=Help.ZDNA.GTAC)
        self.zdna_analyse.add_argument("--at", type=float, default=0, help=Help.ZDNA.AT)
        self.zdna_analyse.add_argument("--msp", "--min-score-percentage", type=float, default=12, help=Help.ZDNA.MSP)
        self.zdna_analyse.add_argument("--tags", nargs="*", help=Help.ZDNA.TAGS)

    def _show_parser(self):
        self.zdna_load = self.zdna_sub.add_parser("show", help=Help.ZDNA.SHOW)
        self.zdna_load.add_argument("result", help=Help.ZDNA.RESULT)
        self.zdna_load.add_argument("--details", "-d", action="store_true", help=Help.ZDNA.DETAILS)

    def _delete_parser(self):
        self.zdna_delete = self.zdna_sub.add_parser("delete", help=Help.ZDNA.DELETE)
        self.zdna_delete.add_argument("result", help=Help.ZDNA.RESULT)

    def _export_parser(self):
        self.zdna_export = self.zdna_sub.add_parser("export", help=Help.ZDNA.EXPORT)
        self.zdna_export.add_argument("result", help=Help.ZDNA.RESULT)
        self.zdna_export.add_argument("--path", "-p", default="./", help=Help.ZDNA.PATH)