from spyne.model.complex import Array, Iterable, ComplexModel
from spyne.model.primitive import Integer, Float, Unicode, Boolean, String

class User(ComplexModel):
    userid = Integer
    username = Unicode
