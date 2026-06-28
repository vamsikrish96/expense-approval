from config import ErrorCode, ERROR_MESSAGES


class APIException(Exception):
    def __init__(self, error_code: ErrorCode, message: str = None, status_code: int = None):
        self.error_code = error_code
        if message is None:
            error_msg = ERROR_MESSAGES.get(error_code)
            if error_msg:
                self.message = error_msg.message
                self.status_code = error_msg.status_code
            else:
                self.message = "An error occurred"
                self.status_code = 500
        else:
            self.message = message
            self.status_code = status_code or 400
        super().__init__(self.message)


class ValidationError(APIException):
    def __init__(self, error_code: ErrorCode, message: str = None):
        super().__init__(error_code, message)


class UnauthorizedError(APIException):
    def __init__(self, message: str = None):
        super().__init__(ErrorCode.UNAUTHORIZED, message)


class ForbiddenError(APIException):
    def __init__(self, message: str = None):
        super().__init__(ErrorCode.FORBIDDEN, message)


class NotFoundError(APIException):
    def __init__(self, message: str = None):
        super().__init__(ErrorCode.CLAIM_NOT_FOUND, message)


class StateTransitionError(APIException):
    def __init__(self, message: str = None):
        super().__init__(ErrorCode.INVALID_STATE_TRANSITION, message)


class SelfApprovalError(APIException):
    def __init__(self, message: str = None):
        super().__init__(ErrorCode.SELF_APPROVAL_NOT_ALLOWED, message)


class InvalidTokenError(APIException):
    def __init__(self, message: str = None):
        super().__init__(ErrorCode.INVALID_TOKEN, message)


class MissingTokenError(APIException):
    def __init__(self, message: str = None):
        super().__init__(ErrorCode.MISSING_TOKEN, message)
