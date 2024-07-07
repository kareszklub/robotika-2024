from utils import clamp

class PID:
    sp: float

    P: float
    I: float
    D: float

    integr_min: float
    integr_max: float

    _prev_err: float
    _integr: float

    def __init__(self, sp: float, p: float, i: float, d: float, integr_min: float, integr_max: float):
        self.sp = sp
        self.P = p
        self.I = i
        self.D = d
        self.integr_min = integr_min
        self.integr_max = integr_max

        self._prev_err = 0
        self._integr = 0

    def compute(self, pv: float, dt: float) -> float:
        err = self.sp - pv

        self._integr = clamp(self._integr + err * dt, self.integr_min, self.integr_max)

        der = (err - self._prev_err) / dt

        self._prev_err = err

        return self.P * err + self.I * self._integr + self.D * der
