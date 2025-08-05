# zdna_facade.py

from dna_ibp.facades.analyse_facade import Analyse

class ZDna(Analyse):
    def analyse(self, 
        sequence: str,
        tags,
        min_sequence_size: int = 10,
        model: str = "model1",
        GC_score: float = 25,
        GTAC_score: float = 3,
        AT_score: float = 0,
        min_score_percentage: float = 12,
        ):
        """
        Facade method for the Z-DNA hunter analyse_creator API method.
        """
        loaded_seq = self.sequence.load(value=sequence)

        return self.api.zdna.analyse_creator(
            sequence=loaded_seq,
            tags=tags,
            min_sequence_size=min_sequence_size,
            model=model,
            GC_score=GC_score,
            GTAC_score=GTAC_score,
            AT_score=AT_score,
            oth_score=0,
            min_score_percentage=min_score_percentage)
    
    @property
    def source_tool(self):
        return self.api.zdna
    
    def load(self, value, verbose=0):
        """
        Facade method for the Z-DNA hunter load API method.
        """
        return super().load(value=value, verbose=verbose)
    
    def result(self, result: str):
        """
        Facade method for the Z-DNA hunter load_results API method.
        """
        return super().result(result=result)

    def delete(self, result: str):
        """
        Facade method for the Z-DNA hunter delete API method.
        """
        return super().delete(result=result)
    
    def export(self, result: str, path: str):
        """
        Facade method for the Z-DNA hunter export API method.
        """
        return super().export(result=result, path=path)