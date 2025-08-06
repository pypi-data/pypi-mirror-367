import sys


def hello():
    """Example function to test the extension."""
    print("Hello function called", file=sys.stderr)
    return "Hello from ReproLab!"

def add(a, b):
    """Return the sum of a and b."""
    return a + b 
