# cpx_parser.py

from dna_ibp.help import Help

class CpXParser:
    def __init__(self, subparsers):
        self.cpx = subparsers.add_parser("cpx", help=Help.CPX.CPX)
        self.cpx_sub = self.cpx.add_subparsers(dest="subcommand")

        self._analyse_parser()
        self._show_parser()
        self._delete_parser()
        self._export_parser()

    def _analyse_parser(self):
        self.cpx_analyse = self.cpx_sub.add_parser("analyse", help=Help.CPX.ANALYSE)
        self.cpx_analyse.add_argument("sequence", help=Help.CPX.SEQUENCE)
        self.cpx_analyse.add_argument("--ws", "--window-size","-w", type=int, default=200, help=Help.CPX.WS)
        self.cpx_analyse.add_argument("--gcp","--gc-percentage", "-g",type=float, default=0.5, help=Help.CPX.GCP)
        self.cpx_analyse.add_argument("--o-e-cpg","--observed-expected-cpg" "-o", type=float, default=0.6, help=Help.CPX.O_E_CPG)
        self.cpx_analyse.add_argument("--gap", "--island-merge-gap","-i", type=int, default=100, help=Help.CPX.ISLAND_MERGE_GAP)
        self.cpx_analyse.add_argument("--second", "-s", type=str, default="G", help=Help.CPX.SECOND_NUCLEOTIDE)
        self.cpx_analyse.add_argument("--tags", "-t", nargs="*", help=Help.CPX.TAGS)
        
    def _show_parser(self):
        self.cpx_load = self.cpx_sub.add_parser("show", help=Help.CPX.SHOW)
        self.cpx_load.add_argument("result", help=Help.CPX.RESULT)
        self.cpx_load.add_argument("--details", "-d", action="store_true", help=Help.CPX.DETAILS)

    def _delete_parser(self):
        self.cpx_delete = self.cpx_sub.add_parser("delete", help=Help.CPX.DELETE)
        self.cpx_delete.add_argument("result", help=Help.CPX.RESULT)

    def _export_parser(self):
        self.cpx_export = self.cpx_sub.add_parser("export", help=Help.CPX.EXPORT)
        self.cpx_export.add_argument("result", help=Help.CPX.RESULT)
        self.cpx_export.add_argument("--path", "-p", default="./", help=Help.CPX.PATH)