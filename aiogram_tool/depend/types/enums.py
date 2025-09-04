from enum import Enum, auto


class Scope(Enum):
     """
     APP: Caching the result for the entire duration of the application
     \nREQUEST: New result for every request
     """
     APP = auto()
     REQUEST = auto()
     