class Error(Exception):
    """Base class for other exceptions"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class BadRow(Exception):
    pass


class BadFile(Exception):
    pass


class BadModel(Exception):
    pass


class BadColumn(Exception):
    pass


class BadValue(Exception):
    pass
