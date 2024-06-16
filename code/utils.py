
def clamp(f: float, mn: float, mx: float) -> float:
	if f < mn:
		return mn
	if f > mx:
		return mx
	return f

def rgb_rel(c: int, r: int, g: int, b: int) -> tuple[float, float, float]:
    if c == 0:
        return 0, 0, 0
    return r / c, g / c, b / c

def rgb_to_hsv(r: float, g: float, b: float) -> float:
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    diff = cmax - cmin

    if cmax == cmin:
        h = 0
    elif cmax == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif cmax == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    elif cmax == b:
        h = (60 * ((r - g) / diff) + 240) % 360

    if cmax == 0:
        s = 0
    else: 
        s = (diff / cmax) * 100

    v = cmax * 100

    return h, s, v
