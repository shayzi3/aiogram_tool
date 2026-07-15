from enum import Enum, auto


class Scope(Enum):
     SINGLETON = auto()
     REQUEST = auto()
     TRANSIENT = auto()
     