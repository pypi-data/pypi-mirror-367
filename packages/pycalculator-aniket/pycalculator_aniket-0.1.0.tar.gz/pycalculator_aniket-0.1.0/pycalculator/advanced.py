import math

def power(a, b): return a ** b

def mod(a, b): return a % b

def factorial(n):
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    return math.factorial(n)

def sqrt(n):
    if n < 0:
        raise ValueError("Cannot take square root of negative number")
    return math.sqrt(n)
