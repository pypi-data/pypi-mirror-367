# p53_facade.py

from dna_ibp.facades.tool_facade import Tool

class P53(Tool):

    def __init__(self, api):
        super().__init__(api=api)

    def run(self, **kwargs):
        """
        Facade method for the run API function of P53 predictor tool.
        """
        sequence = kwargs.get("sequence")

        if len(sequence) == 1:
            df = self.api.p53_predictor.run(sequence=sequence[0])
            print(df.to_string())
        else:
            df = self.api.p53_predictor.run_multiple(sequences=sequence)
            print(df.to_string())