"""
Custom exceptions.
"""


class CubaBaseException(Exception):
    pass


class UserActivatedException(CubaBaseException):
    pass


class NoLicenseException(CubaBaseException):
    pass


class LicenseNotValidException(CubaBaseException):
    pass


class RestApiNotAvailableexception(CubaBaseException):
    pass
