
def clamp(f, mn, mx):
	if f < mn:
		return mn
	if f > mx:
		return mx
	return f

def rgb_rel(c: int, r: int, g: int, b: int) -> tuple[float, float, float]:
    if c == 0:
        return 0, 0, 0
    return r / c, g / c, b / c

def rgb_to_hsv(r: float, g: float, b: float) -> tuple[float, float, float]:
    '''HSV to RGB

    h: 0.0 - 360.0
    s: 0.0 - 1.0
    v: 0.0 - 1.0
    '''

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

def hsv_to_rgb(h: float, s: float, v: float) -> tuple[float, float, float]:
    h %= 360

    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if 0 <= h and h < 60:
        rgb = c, x, 0
    elif 60 <= h and h < 120:
        rgb = x, c, 0
    elif 120 <= h and h < 180:
        rgb = 0, c, x
    elif 180 <= h and h < 240:
        rgb = 0, x, c
    elif 240 <= h and h < 300:
        rgb = x, 0, c
    else:
        rgb = c, 0, x

    r, g, b = rgb
    return r + m, g + m, b + m
