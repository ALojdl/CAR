"""
    Contains classes representing custom made exceptions.
"""

# Main exception class


class CustomError(Exception):
    """    Base custom made exception class.    """
    pass


class FoursquareError(CustomError):
    """    Raised when there is some kind of Foursquare error.    """
    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

