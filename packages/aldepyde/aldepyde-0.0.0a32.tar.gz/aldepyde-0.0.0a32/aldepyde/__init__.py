__version__ = "0.0.0a2"
__author__ = "Nate McMurray"
__description__ = "A module for mangling biomolecules"

from ._config import _configuration
from aldepyde.cache.cachemanager import CacheManager


_cache_manager = CacheManager(initialize=False)
def create_cache(max_memory="2gib") -> CacheManager:
    global _cache_manager
    _cache_manager = _cache_manager(max_memory=max_memory,
                                    initialize=True)
    return _cache_manager

def get_cache() -> CacheManager:
    global _cache_manager
    return _cache_manager

# def get_cache() -> _cache_handler:
#     global _cache
#     # if _cache.null:
#     #     return create_cache()
#     return _cache

# def SaveConfig(path: str="config.json", indent: str = "") -> None:
#     global _config
#     get_config().Save(path=path, indent=indent)
#
#
# def LoadConfig(s: dict | str, ignore_missing=False) -> None:
#     global _config
#     get_config().Load(s, ignore_missing=ignore_missing)


# from . import rand
# from . import biomolecule
# from . import fetcher

from importlib import import_module

__all__ = ["rand", "biomolecule", "fetcher"]

def __getattr__(name):
    if name in __all__:
        return import_module(f".{name}", __name__)
    raise AttributeError(name)

def __dir__():
    return sorted(list(globals().keys()) + __all__)