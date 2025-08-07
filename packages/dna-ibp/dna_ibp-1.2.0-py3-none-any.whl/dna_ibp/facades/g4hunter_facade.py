# g4hunter_facade.py

from dna_ibp.facades.analyse_facade import Analyse

class G4Hunter(Analyse):
    def analyse(self, sequence: str, threshold: float, window_size: int, tags: str | None):
        """
        Facade method for the G4Hunter analyse_creator API method.
        """
        loaded_seq = self.sequence.load(value=sequence)
        return self.api.g4hunter.analyse_creator(tags=tags, sequence=loaded_seq, threshold=threshold, window_size=window_size)
    
    @property
    def source_tool(self):
        return self.api.g4hunter
    
    def load(self, value, verbose=0):
        """
        Facade method for the G4Hunter load API method.
        """
        return super().load(value=value, verbose=verbose)
    
    def result(self, result: str):
        """
        Facade method for the G4Hunter load_results API method.
        """
        return super().result(result=result)

    def delete(self, result: str):
        """
        Facade method for the G4Hunter delete API method.
        """
        return super().delete(result=result)
    
    def export(self, result: str, path: str, aggregate: bool):
        """
        Facade method for the G4Hunter export API method.
        """
        ld_result = self.load(value=result)
        self.source_tool.export_csv(analyse=ld_result, path=path, aggregate=aggregate)