from enum import Enum, auto


class Scope(Enum):
     """Scopes for dependecies

     Args:
         SINGLETON - caching of the dependency result at the full lifecycle level
         REQUEST - caching of a dependency result at the level of a single user request
         TRANSIENT - Dependence is triggered every time.
     """
     SINGLETON = auto()
     REQUEST = auto()
     TRANSIENT = auto()
     