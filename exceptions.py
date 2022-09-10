# Exceptions for more readable code

class InvalidCategoryError(Exception):
    pass


class InvalidNewPixelValues(Exception):
    pass


class WrongDateError(Exception):
    pass


class ValuesDoNotMatchException(Exception):
    pass


class WrongTokenException(Exception):
    pass


class InvalidEmailException(Exception):
    pass


class SameCategoriesException(Exception):
    pass
