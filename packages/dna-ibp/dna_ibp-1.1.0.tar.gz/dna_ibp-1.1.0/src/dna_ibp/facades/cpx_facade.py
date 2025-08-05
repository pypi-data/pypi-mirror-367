# cpx_facade.py

from dna_ibp.facades.analyse_facade import Analyse

class CpX(Analyse):
    def analyse(self, 
        sequence: str,
        tags,
        min_window_size: int = 200,
        min_gc_percentage: float = 0.5,
        min_obs_exp_cpg: float = 0.6,
        min_island_merge_gap: int = 100,
        second_nucleotide: str = "G"
        ):
        """
        Facade method for the CpX hunter analyse_creator API method.
        """
        loaded_seq = self.sequence.load(value=sequence)

        return self.api.cpg.analyse_creator(
            sequence=loaded_seq,
            tags=tags,
            min_window_size=min_window_size,
            min_gc_percentage=min_gc_percentage,
            min_obs_exp_cpg=min_obs_exp_cpg,
            min_island_merge_gap=min_island_merge_gap,
            second_nucleotide=second_nucleotide
            )
    
    @property
    def source_tool(self):
        return self.api.cpg
    
    def load(self, value, verbose=0):
        """
        Facade method for the CpX hunter load API method.
        """
        return super().load(value=value, verbose=verbose)
    
    def result(self, result: str):
        """
        Facade method for the CpX hunter load_results API method.
        """
        return super().result(result=result)

    def delete(self, result: str):
        """
        Facade method for the CpX hunter delete API method.
        """
        return super().delete(result=result)
    
    def export(self, result: str, path: str):
        """
        Facade method for the CpX hunter export API method.
        """
        return super().export(result=result, path=path)