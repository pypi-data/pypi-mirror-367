"""
Helper classes for writing fully compatible NumPy/JaX code.
The goal is that code written for JaX should degrade gracefully to using pure
NumPy operations if JaX is unavailable. (Or removed, e.g. for profiling.)

We expect users who want this graceful degradation to also use the high-level
`jax.numpy` module. This makes our problem already 99% solved, since for most
things we can just redirect ``jnp.<op>`` to ``np.<op>``.

.. Important:: The array type created with `jnp.array` is a subclass of the
   standard NumPy array, augmented with additional JaX methods. This is what
   allows operations like ``A.at[idx].set(value)`` to be transparently
   translated to a NumPy-compatible form.

"""

import numpy as np
from functools import wraps

def __getattr__(attr):
    try:
        return ufunc_dict[attr]
    except KeyError:
        return getattr(np, attr)

## Ufuncs which return arrays with .at method ##

def ufunc_wrapper(ufunc):
    @wraps(ufunc)
    def wrapper(*args, **kwds):
        return array(ufunc(*args, **kwds))
    return wrapper
ufunc_dict = {nm: ufunc_wrapper(obj)
              for nm, obj in np.__dict__.items()
              if isinstance(obj, np.ufunc)}

## Array with .at method ##
# C.f. https://numpy.org/doc/stable/user/basics.subclassing.html#slightly-more-realistic-example-attribute-added-to-existing-array

class array(np.ndarray):
    """
    Substitute for `numpy.array` which adds the `at` method for
    purely-function in-place operations.
    """
    def __new__(cls, input_array, *args, **kwds):
        obj = np.asarray(input_array, *args, **kwds).view(cls)
        obj.at = _AtConstructor(obj)
        return obj
    def __array_finalize__(self, obj):
        if obj is None: return
        self.at = _AtConstructor(self)
        # at_constructor = getattr(obj, "at", None)
        # if at_constructor is None:
        #     # (Probably) attaching an `.at` method to a plain NumPy array: we need to create a new one
        #     self.at = _AtConstructor(obj)
        # else:
        #     import pdb; pdb.set_trace()
        #     self.at = at_constructor

class _AtConstructor:
    def __init__(self, owner):
        self.owner = owner
    def __getitem__(self, key):
        return _AtOp(self.owner, key)
        
class _AtOp:
    def __init__(self, owner, key):
        self.owner = owner
        self.key = key
    def set(self, value):
        self.owner[self.key] = value
        return self.owner
    def add(self, value):
        self.owner[self.key] += value
        return self.owner
    def multiply(self, value):
        self.owner[self.key] *= value
        return self.owner


# ## Wrapped functions ##

# def tile(*args, **kwds):
#     A = np.tile(*args, **kwargs)
#     A.at = 

def concatenate(*args, **kwds):
    return array(np.concatenate(*args, **kwds))

def empty_like(*args, **kwds):
    return array(np.empty_like(*args,**kwds))