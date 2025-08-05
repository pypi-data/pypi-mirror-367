# __init__.py

from dna_ibp.facades.sequence_facade import Sequence
from dna_ibp.facades.g4hunter_facade import G4Hunter
from dna_ibp.facades.rloop_facade import Rloop
from dna_ibp.facades.g4killer_facade import G4Killer
from dna_ibp.facades.p53_facade import P53
from dna_ibp.facades.zdna_facade import ZDna
from dna_ibp.facades.cpx_facade import CpX

__all__ = ["Facades"]

class Facades:
    def __init__(self, api):
        self.sequence = Sequence(api=api)
        self.g4hunter = G4Hunter(api=api, SeqObj=self.sequence)
        self.rloop = Rloop(api=api, SeqObj=self.sequence)
        self.zdna = ZDna(api=api, SeqObj=self.sequence)
        self.cpx = CpX(api=api, SeqObj=self.sequence)
        self.g4killer = G4Killer(api=api)
        self.p53 = P53(api=api)

