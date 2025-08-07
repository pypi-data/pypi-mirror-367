# sequence_parser.py

import argparse
import pathlib
from dna_ibp.help import Help

class SequenceParser:
    def __init__(self, subparsers):
        self.seq_parser = subparsers.add_parser("sequence", help=Help.SEQUENCE.SEQUENCE)
        self.seq_subparsers = self.seq_parser.add_subparsers(dest="subcommand")

        self._create_parser()
        self._show_parser()
        self._data_parser()
        self._delete_parser()
        self._count_parser()

    def _create_parser(self) -> None:
        self.seq_upload_parser = self.seq_subparsers.add_parser("create", help=Help.SEQUENCE.UPLOAD)
        self.upload_choices = self.seq_upload_parser.add_mutually_exclusive_group(required=True)
        self.upload_choices.add_argument("--file", "-f", type=pathlib.Path ,help=Help.SEQUENCE.FILE)
        self.upload_choices.add_argument("--id", "-i", help=Help.SEQUENCE.ID)
        self.upload_choices.add_argument("--text", "-t", type=str, help=Help.SEQUENCE.TEXT)
        
        self.seq_upload_parser.add_argument("--circular", action=argparse.BooleanOptionalAction, default=True, help=Help.SEQUENCE.CIRCULAR)
        self.seq_upload_parser.add_argument("--tags", nargs="*", help=Help.SEQUENCE.TAGS)
        self.seq_upload_parser.add_argument("--nucleic", choices=["DNA","RNA"], default="DNA", help=Help.SEQUENCE.NUCL_TYPE)
        self.seq_upload_parser.add_argument("--name", "-n", type=str, help=Help.SEQUENCE.NAME)

    def _show_parser(self) -> None:
        self.seq_load_parser = self.seq_subparsers.add_parser("show", help=Help.SEQUENCE.LOAD)
        self.seq_load_parser.add_argument("sequence", help=Help.SEQUENCE.SEQ)

    def _data_parser(self) -> None:
        self.seq_data_parser = self.seq_subparsers.add_parser("data")
        self.seq_data_parser.add_argument("sequence", help=Help.SEQUENCE.SEQ)
        self.seq_data_parser.add_argument("--length", "-l", type=int, default=100)
        self.seq_data_parser.add_argument("--position", "-p", type=int, default=0)

    def _delete_parser(self) -> None:
        self.seq_delete_parser = self.seq_subparsers.add_parser("delete", help=Help.SEQUENCE.DELETE)
        self.seq_delete_parser.add_argument("sequence", help=Help.SEQUENCE.SEQ)

    def _count_parser(self) -> None:
        self.seq_count_parser = self.seq_subparsers.add_parser("count", help=Help.SEQUENCE.NUCL_COUNT)
        self.seq_count_parser.add_argument("sequence", help=Help.SEQUENCE.SEQ)
