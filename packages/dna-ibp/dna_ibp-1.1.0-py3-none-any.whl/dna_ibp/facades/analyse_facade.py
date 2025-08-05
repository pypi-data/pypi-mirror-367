# analyse_facade.py
# facade parent class for DNA analyser tools

from abc import ABCMeta, abstractmethod
from dna_ibp.utils import is_valid_uuid, is_int_or_slice, parse_slice, format_dataframe
from dna_ibp.facades.sequence_facade import Sequence
import shutil

class Analyse(metaclass=ABCMeta):

    def __init__(self, api, SeqObj: Sequence):
        self.api = api
        self.sequence = SeqObj
    
    @abstractmethod
    def analyse(self):
        raise NotImplementedError("Not implemented.")
        
    @property
    @abstractmethod
    def source_tool(self):
        """
        Tool subclasses must override this method to provide the correct data source.
        """
        raise NotImplementedError("Child class must define source_tool.")
    
    def load(self, value: str, verbose: bool = True):
        if value == "all":
            df = self.source_tool.load_all()

        elif is_valid_uuid(value):
            df = self.source_tool.load_by_id(id=value)

        elif is_int_or_slice(value):
            indices = parse_slice(value)
            df = self.source_tool.load_all().iloc[indices]

        else:
            df = self.source_tool.load_all(tags=value)

        if verbose == True:    
            format_dataframe(df_or_ser=df)

        return df
    
    def result(self, result: str):
        ld_result = self.load(value=result, verbose=False)
        df = self.source_tool.load_results(analyse=ld_result)
        
        format_dataframe(df_or_ser=df)
        
        return df

    @abstractmethod
    def delete(self, result: str):
        ld_result = self.load(value=result, verbose=False)
        return self.source_tool.delete(analyse=ld_result)
    
    def export(self, result: str, path: str):
        ld_result = self.load(value=result, verbose=False)
        self.source_tool.export_csv(analyse=ld_result, path=path)