# g4killer_facade.py

from dna_ibp.facades.tool_facade import Tool

class G4Killer(Tool):
    
    def __init__(self, api):
        super().__init__(api=api)

    def run(self, **kwargs):
        """
        Facade method for the run API function of G4Killer tool.
        """
        sequence = kwargs.get("sequence")
        complementary = kwargs.get("complementary")
        threshold = kwargs.get("threshold")

        if len(sequence) == 1:
            df = self.api.g4killer.run(sequence=sequence[0], complementary=complementary, threshold=threshold)
            print(df.to_string())
        else:
            df = self.api.g4killer.run_multiple(sequences=sequence, complementary=complementary, threshold=threshold)
            print(df.to_string())