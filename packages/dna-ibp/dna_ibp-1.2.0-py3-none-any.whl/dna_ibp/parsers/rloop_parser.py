# rloop_parser.py

from dna_ibp.help import Help

class RloopParser:
    def __init__(self, subparsers):
        self.rloop = subparsers.add_parser("rloop", help=Help.RLOOP.RLOOP)
        self.rloop_sub = self.rloop.add_subparsers(dest="subcommand")

        self._analyse_parser()
        self._show_parser()
        self._delete_parser()
        self._export_parser()

    def _analyse_parser(self):
        self.rloop_analyse = self.rloop_sub.add_parser("analyse", help=Help.RLOOP.ANALYSE)
        self.rloop_analyse.add_argument("sequence", help=Help.RLOOP.SEQUENCE)
        self.rloop_analyse.add_argument("--riz3g", action="store_true", default=False, help=Help.RLOOP.RIZ3G)
        self.rloop_analyse.add_argument("--riz4g", action="store_true", default=False, help=Help.RLOOP.RIZ4G)
        self.rloop_analyse.add_argument("--tags", nargs="*", help=Help.RLOOP.TAGS)

    def _show_parser(self):
        self.rloop_load = self.rloop_sub.add_parser("show", help=Help.RLOOP.SHOW)
        self.rloop_load.add_argument("result", help=Help.RLOOP.RESULT)
        self.rloop_load.add_argument("--details", "-d", action="store_true", help=Help.RLOOP.DETAILS)
        
    def _delete_parser(self):
        self.rloop_delete = self.rloop_sub.add_parser("delete", help=Help.RLOOP.DELETE)
        self.rloop_delete.add_argument("result", help=Help.RLOOP.RESULT)

    def _export_parser(self):
        self.rloop_export = self.rloop_sub.add_parser("export", help=Help.RLOOP.EXPORT)
        self.rloop_export.add_argument("result", help=Help.RLOOP.RESULT)
        self.rloop_export.add_argument("--path", "-p", default="./", help=Help.RLOOP.PATH)