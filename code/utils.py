
def clamp(f: float, mn: float, mx: float) -> float:
	if f < mn:
		return mn
	if f > mx:
		return mx
	return f
