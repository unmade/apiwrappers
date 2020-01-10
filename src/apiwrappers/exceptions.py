class DriverError(Exception):
    pass


class ConnectionFailed(DriverError):
    pass


class Timeout(DriverError):
    pass
