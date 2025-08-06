import math

def sin(x): return math.sin(math.radians(x))

def cos(x): return math.cos(math.radians(x))

def tan(x):
    if (x - 90) % 180 == 0:
        raise ValueError("tan is undefined at 90 + k*180 degrees")
    return math.tan(math.radians(x))
