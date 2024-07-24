
from math import ceil, floor, pow, modf, trunc

class DbgNum:
    _val: int | float
    __doc__ = '<black magic>'

    def __init__(self, v: int | float): self._val = v
    def update(v: int | float): self._val = v

    def __abs__(self):    return abs(self._val)
    def __add__(self, x): return self._val + x
    def __and__(self, x): return self._val and x
    def __bool__(self):   return bool(self._val)
    def __ceil__(self):   return ceil(self._val)
    def __divmod__(self, x): return (self._val // x, self._val % x)
    def __eq__(self, o): return self._val == o
    def __float__(self): return float(self._val)
    def __floor__(self): return floor(self._val)
    def __floordiv__(self, x): return self._val // x
    def __format__(self, f): return format(self._val, f)
    def __ge__(self, x): return self._val >= x
    def __gt__(self, x): return self._val > x
    def __hash__(self): return hash(self._val)
    def __index__(self): return int(self)
    def __int__(self): return int(self._val)
    def __invert__(self): return not self._val
    def __le__(self, x): return self._val < x
    def __lshift__(self, x): return self._val << x
    def __lt__(self, x): return self._val < x
    def __mod__(self, x): return self._val % x 
    def __mul__(self, x): return self._val * x
    def __ne__(self, x): return self._val != x
    def __neg__(self): return -self._val
    def __or__(self, x): return self._val or x
    def __pos__(self): return +self._val
    def __pow__(self, x): return self._val ** x
    def __radd__(self, x): return x + self._val
    def __rand__(self, x): return x and self._val
    def __rdivmod__(self, x): return (x // self._val, x % self._val)
    def __repr__(self): return repr(self._val)
    def __rfloordiv__(self, x): return x // self._val
    def __rlshift__(self, x): return x << self._val
    def __rmod__(self, x): return x % self._val
    def __rmul__(self, x): return x * self._val
    def __ror__(self, x): return x or self._val
    def __round__(self): return round(self._val)
    def __rpow__(self, x): return x ** self._val
    def __rrshift__(self, x): return x >> self._val
    def __rshift__(self, x): return self._val >> x
    def __rsub__(self, x): return x - self._val
    def __rtruediv__(self, x): return x / self._val
    def __rxor__(self, x): return x ^ self._val
    def __str__(self): return str(self._val)
    def __sub__(self, x): return self._val - x
    def __matmul__(self, x): return self._val @ x
    def __truediv__(self, x): return self._val / x
    def __trunc__(self): return trunc(self._val)
    def __xor__(self, x): return self._val ^ x
    def to_bytes(self, l, o): return self._val.to_bytes(l, o)
    def __iadd__(self, b): self._val += b
    def __iand__(self, b): self._val &= b
    def __ifloordiv__(self, b): self._val //= b
    def __ilshift__(self, b): self._val <<= b
    def __imod__(self, b): self._val %= b
    def __imul__(self, b): self._val *= b
    def __imatmul__(self, b): self._val @= b
    def __ior__(self, b): self._val |= b
    def __ipow__(self, b): self._val **= b
    def __irshift__(self, b): self._val >>= b
    def __isub__(self, b): self._val -= b
    def __itruediv__(self, b): self._val /= b
    def __ixor__(self, b): self._val ^= b
