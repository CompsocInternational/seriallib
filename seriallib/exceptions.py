class ArmException(Exception):
    pass

class ArmRetryLimitExceededException(ArmException):
    pass

class ArmUnknownOrUnexpectedResponseException(ArmException):
    pass