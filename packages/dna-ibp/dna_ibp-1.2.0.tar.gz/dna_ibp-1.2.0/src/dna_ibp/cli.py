#!/usr/bin/env python3

import os
import tempfile
import time

from DNA_analyser_IBP.api import Api
from DNA_analyser_IBP.utils import Logger
from dna_ibp.facades import Facades
from dna_ibp.parsers import Parsers
from io import StringIO
from contextlib import redirect_stdout

class DnaCli:
    """
    Main class for the DNA analyser CLI parser
    """

    def __init__(self, email=None, password=None):
        self.api = None
        self.handle_login(email=email, password=password)

        self.facade = Facades(api=self.api)
        self.parser = Parsers()

    def dispatch_command(self, command: str):
        command_map = {
            "sequence": self.sequence_logic,
            "g4hunter": self.g4hunter_logic,
            "g4killer": self.g4killer_logic,
            "p53": self.p53_logic,
            "rloop": self.rloop_logic,
            "zdna": self.zdna_logic,
            "cpx": self.cpx_logic,
        }

        return command_map.get(command)

    def handle_login(self, email=None, password=None) -> None:
        TIMEOUT = 60 * 60

        def _retrieve_token() -> tuple:
            with open(self.temp_file_path, "r") as f:
                filelines = f.readlines()
                stored_email = filelines[0].strip()
                stored_jwt = filelines[1].strip()
            return stored_email, stored_jwt

        def _create_api(email=None, password=None) -> None:
            if email and password:
                self.api = Api(email=email, password=password)
            else:
                self.api = Api()

            try:
                user_email = self.api._Api__user.__dict__.get("email")
            except AttributeError:
                Logger.error("Wrong username or password!")
                quit()
                
            jwt = self.api._Api__user.__dict__.get("jwt")
            with open(self.temp_file_path, "w") as f:
                f.write(user_email + "\n")
                f.write(jwt + "\n")

        self.temp_file_path = os.path.join(tempfile.gettempdir(), "ibp_credentials.txt")

        if email and password:
            # Skip cache and login directly with provided credentials
            return _create_api(email=email, password=password)

        if os.path.exists(self.temp_file_path):
            file_creation_time = os.path.getmtime(self.temp_file_path)
            current_time = time.time()

            if current_time - file_creation_time > TIMEOUT:
                os.remove(self.temp_file_path)
                return _create_api()

            stored_email, jwt = _retrieve_token()
            with redirect_stdout(StringIO()):
                self.api = Api(email="host", password="host")  # Dummy credentials just to init

            self.api._Api__user.__dict__["email"] = stored_email
            self.api._Api__user.__dict__["jwt"] = jwt
        else:
            return _create_api()
        
    def reset_login(self) -> None:
        """
        Function for manual login reset

        Returns: None
        """
        self.temp_file_path = os.path.join(tempfile.gettempdir(), "ibp_credentials.txt")
        os.remove(self.temp_file_path)
        
        Logger.info(f"User {self.api._Api__user.email} logged out...")

    # Section for tool logic. Return values exist for testing purposes.
    def sequence_logic(self, args):
        """Handles the sequence manipulation logic"""
        if args.subcommand == "show":
            seq_response = self.facade.sequence.load(value=args.sequence, verbose=True)
        elif args.subcommand == "data":
            seq_response = self.facade.sequence.data(seq=args.sequence, length=args.length, position=args.position)
        elif args.subcommand == "delete":
            seq_response = self.facade.sequence.delete(seq=args.sequence)
        elif args.subcommand == "create":
            seq_response = self.facade.sequence.create(
                file = args.file,
                id = args.id,
                text = args.text,
                circular = args.circular,
                tags = args.tags,
                nucleic = args.nucleic,
                name = args.name
            )
        elif args.subcommand == "count":
            seq_response = self.facade.sequence.count(seq=args.sequence)
        
        return seq_response

    def g4hunter_logic(self, args):
        """Handles the g4hunter command logic."""
        if args.subcommand == "analyse":
            g4hunter_response = self.facade.g4hunter.analyse(sequence=args.sequence, threshold=args.threshold, window_size=args.windowsize, tags=args.tags)
        elif args.subcommand == "show":
            if args.details:
                details_response = self.facade.g4hunter.result(result=args.result)
                return details_response
            g4hunter_response = self.facade.g4hunter.load(value=args.result, verbose=True)
        elif args.subcommand == "delete":
            g4hunter_response = self.facade.g4hunter.delete(result=args.result)
        elif args.subcommand == "export":
            g4hunter_response = self.facade.g4hunter.export(result=args.result, path=args.path, aggregate=args.aggregate)

        return g4hunter_response
  
    def g4killer_logic(self, args):
        """Handles the g4killer command logic."""

        if args.subcommand == "run":
            g4killer_response = self.facade.g4killer.run(sequence=args.sequence, complementary=args.complementary, threshold=args.threshold)

        return g4killer_response

    def p53_logic(self, args):
        """
        Handles the p53 command logic.
        """

        if args.subcommand == "run":
            p53_response = self.facade.p53.run(sequence=args.sequence)

        return p53_response

    def rloop_logic(self, args):
        """Handles the rloop command logic."""
        if args.subcommand == "analyse":
            rloop_response = self.facade.rloop.analyse(sequence=args.sequence, riz_3g=args.riz3g, riz_4g=args.riz4g, tags=args.tags)
        elif args.subcommand == "show":
            if args.details:
                rloop_response = self.facade.rloop.result(result=args.result)
                return rloop_response
            rloop_response = self.facade.rloop.load(value=args.result, verbose=True)
        elif args.subcommand == "delete":
            rloop_response = self.facade.rloop.delete(result=args.result)
        elif args.subcommand == "export":
            rloop_response = self.facade.rloop.export(result=args.result, path=args.path)

        return rloop_response
            
    def zdna_logic(self, args):
        """Handles the zdna command logic."""
        if args.subcommand == "analyse":
            zdna_response = self.facade.zdna.analyse(
                sequence=args.sequence,
                min_sequence_size=args.mss,
                model=args.model,
                GC_score=args.gc,
                GTAC_score=args.gtac,
                AT_score=args.at,
                min_score_percentage=args.msp,
                tags=args.tags
                )
        elif args.subcommand == "show":
            if args.details:
               zdna_response = self.facade.zdna.result(result=args.result)
               return zdna_response
            zdna_response = self.facade.zdna.load(value=args.result, verbose=True)
        elif args.subcommand == "delete":
            zdna_response = self.facade.zdna.delete(result=args.result)
        elif args.subcommand == "export":
            zdna_response = self.facade.zdna.export(result=args.result, path=args.path)

        return zdna_response
            
    def cpx_logic(self, args):
        """Handles the cpx command logic."""
        if args.subcommand == "analyse":
            cpx_response = self.facade.cpx.analyse(
                sequence=args.sequence,
                tags=args.tags,
                min_window_size=args.ws,
                min_gc_percentage=args.gcp,
                min_obs_exp_cpg=args.o_e_cpg,
                min_island_merge_gap=args.gap,
                second_nucleotide=args.second
                )
        elif args.subcommand == "show":
            if args.details:
                cpx_response = self.facade.cpx.result(result=args.result)
                return cpx_response
            cpx_response = self.facade.cpx.load(value=args.result, verbose=True)
        elif args.subcommand == "delete":
            cpx_response = self.facade.cpx.delete(result=args.result)
        elif args.subcommand == "export":
            cpx_response = self.facade.cpx.export(result=args.result, path=args.path)

        return cpx_response

def main():
    CLI = DnaCli()
    args = CLI.parser.parse_args()

    if args.reset:
        CLI.reset_login()
    else:
        command_func = CLI.dispatch_command(args.command)
        if command_func:
            command_func(args)
        else:
            CLI.parser.print_help()





