import numpy as np
from . import numpy as jnp

def jit(fun, *args, **kwargs):
    """No-op which simply returns the decorated function unchanged."""
    return fun

def device_put(x, device, *, src):
    """
    Converts as plain numpy array to a mocked numpy array, which allows
    use of JaX-only methods like `.at`.
    Any other argument type is returned unchanged.
    """
    if isinstance(x, np.ndarray):
        return x.view(jnp.array)
    else:
        return x