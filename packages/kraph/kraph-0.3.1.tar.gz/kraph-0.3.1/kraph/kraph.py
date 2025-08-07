from koil.composition import Composition

from kraph.rath import KraphRath
from kraph.datalayer import DataLayer


class Kraph(Composition):
    rath: KraphRath
    datalayer: DataLayer
