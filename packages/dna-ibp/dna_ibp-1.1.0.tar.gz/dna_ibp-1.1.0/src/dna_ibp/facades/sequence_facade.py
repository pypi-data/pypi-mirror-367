# sequence_facade.py

from dna_ibp.utils import is_valid_uuid, is_int_or_slice, parse_slice, is_fasta, is_multi_fasta, format_dataframe
import pandas as pd

class Sequence:
    """
    Sequence class containing facade methods for API calls.
    """
    def __init__(self, api):
        self.api = api

    def create(self, **kwargs):
        """
        Facade method for handling sequence creating functions.
        """

        circular = kwargs.get("circular")
        tags = kwargs.get("tags")
        nucleic = kwargs.get("nucleic")
        name = kwargs.get("name")

        if kwargs.get("text"):
            string = kwargs.get("text")
            return self.api.sequence.text_creator(circular=circular, tags=tags, nucleic_type=nucleic, string=string, name=name)

        elif kwargs.get("id"):
            id = kwargs.get("id")
            return self.api.sequence.ncbi_creator(tags=tags, circular=circular, name=name, ncbi_id=id)

        else:
            file_path = kwargs.get("file")
            file_format = "PLAIN"
            if is_fasta(file_path):
                if is_multi_fasta(file_path):
                    return self.api.sequence.multifasta_creator(tags=tags, circular=circular, path=file_path, nucleic_type=nucleic)
                else:
                    file_format = "FASTA"
            
            return self.api.sequence.file_creator(tags=tags, circular=circular, nucleic_type=nucleic, path=file_path, name=name, format=file_format)
            

    def load(self, value: str, verbose: int = 0) -> pd.DataFrame:
        """
        Facade method for handling sequence loading functions.
        """

        if value == "all":
            df = self.api.sequence.load_all()

        elif is_valid_uuid(value):
            df = self.api.sequence.load_by_id(id=value)

        elif is_int_or_slice(value):
            indices = parse_slice(value)
            df = self.api.sequence.load_all().iloc[indices]
            
        else:
            df = self.api.sequence.load_all(tags=value)
        
        if verbose == True:
            format_dataframe(df_or_ser=df)

        return df

    def data(self, seq: str, length: int, position: int):
        """
        Facade method for the load_data API function.
        """
        df = self.api.sequence.load_data(length=length, position=position, sequence=self.load(seq, verbose=False))
        print(f"Chosen sequence:\n {df}")

        return df

    def delete(self, seq: str):
        """
        Facade method for the delete API function.
        """
        self.api.sequence.delete(sequence=self.load(seq, verbose=False))

    def count(self, seq: str):
        """
        Facade method for the nucleic_count API function.
        """
        self.api.sequence.nucleic_count(sequence=self.load(seq, verbose=False))