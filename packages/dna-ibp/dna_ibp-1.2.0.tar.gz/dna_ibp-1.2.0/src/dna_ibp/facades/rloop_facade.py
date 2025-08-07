# rloop_facade.py

from dna_ibp.facades.analyse_facade import Analyse

class Rloop(Analyse):
    def analyse(self, sequence: str, riz_3g: bool, riz_4g: bool, tags: str | None):
        """
        Facade method for the R-loop tracker analyse_creator API method.
        """
        loaded_seq = self.sequence.load(value=sequence)
        return self.api.rloopr.analyse_creator(sequence=loaded_seq, riz_3g_cluster=riz_3g, riz_2g_cluster=riz_4g, tags=tags)
    
    @property
    def source_tool(self):
        return self.api.rloopr
    
    def load(self, value, verbose=0):
        """
        Facade method for the R-loop tracker load API method.
        """
        return super().load(value=value, verbose=verbose)
    
    def result(self, result: str):
        """
        Facade method for the R-loop tracker load_results API method.
        """
        return super().result(result=result)

    def delete(self, result: str):
        """
        Facade method for the R-loop tracker delete API method.
        """
        return super().delete(result=result)
    
    def export(self, result: str, path: str):
        """
        Facade method for the R-loop tracker export API method.
        """
        return super().export(result=result, path=path)