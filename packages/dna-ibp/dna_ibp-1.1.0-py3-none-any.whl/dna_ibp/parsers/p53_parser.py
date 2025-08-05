# p53_parser.py

from dna_ibp.help import Help

class P53Parser:
    def __init__(self, subparsers):
        self.p53_predictor = subparsers.add_parser("p53", help=Help.P53.P53)
        self.p53_sub = self.p53_predictor.add_subparsers(dest="subcommand")

        self._run_parser()

    def _run_parser(self):
        self.p53_run = self.p53_sub.add_parser("run", help=Help.P53.RUN)
        self.p53_run.add_argument("sequence", nargs="+", help=Help.P53.SEQUENCE)