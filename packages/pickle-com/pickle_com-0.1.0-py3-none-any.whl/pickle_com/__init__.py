import pickle as _pickle

def _patch_legacy():
    """make compatibility patch of numpy and inspect."""
    try:
        import numpy as np
        patch_map = {
            'int': np.int32,
            'float': np.float32,
            'bool': np.bool_,
            'complex': complex,
            'object': object,
            'unicode': str,
            'str': str,
        }
        for name, value in patch_map.items():
            if not hasattr(np, name):
                setattr(np, name, value)
    except ImportError:
        pass

    try:
        import inspect
        if not hasattr(inspect, 'getargspec'):
            inspect.getargspec = inspect.getfullargspec
    except ImportError:
        pass

def load(file, *args, **kwargs):
    _patch_legacy()
    return _pickle.load(file, *args, **kwargs)

def loads(s, *args, **kwargs):
    _patch_legacy()
    return _pickle.loads(s, *args, **kwargs)

def load_all(file, *args, **kwargs):
    _patch_legacy()
    if hasattr(_pickle, 'load_all'):
        return _pickle.load_all(file, *args, **kwargs)
    raise NotImplementedError("pickle.load_all not available in this python version")


dump = _pickle.dump
dumps = _pickle.dumps
Pickler = _pickle.Pickler
Unpickler = _pickle.Unpickler
DEFAULT_PROTOCOL = _pickle.DEFAULT_PROTOCOL
HIGHEST_PROTOCOL = _pickle.HIGHEST_PROTOCOL
