
def clamp(f: float, mn: float, mx: float) -> float:
	if f < mn:
		return mn
	if f > mx:
		return mx
	return f

def rgb_rel(crgb: tuple[int, int, int, int]) -> tuple[float, float, float]:
    c, r, g, b = crgb

    if c == 0:
        return 0, 0, 0
    return r / c, g / c, b / c

def rgb_to_hsv(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    '''HSV to RGB

    h: 0.0 - 360.0
    s: 0.0 - 1.0
    v: 0.0 - 1.0
    '''

    r, g, b = rgb

    cmax = max(r, g, b)
    cmin = min(r, g, b)
    diff = cmax - cmin

    if cmax == cmin:
        h = 0
    elif cmax == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif cmax == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else: # elif cmax == b:
        h = (60 * ((r - g) / diff) + 240) % 360

    if cmax == 0:
        s = 0
    else: 
        s = (diff / cmax) * 100

    v = cmax * 100

    return h, s, v
