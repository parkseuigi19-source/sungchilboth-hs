"""
커스텀 예외 클래스 정의
"""


class SungchibotException(Exception):
    """성취봇 기본 예외 클래스"""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(SungchibotException):
    """입력 검증 오류"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class AIServiceError(SungchibotException):
    """AI 서비스 오류"""
    def __init__(self, message: str):
        super().__init__(message, "AI_SERVICE_ERROR")


class DatabaseError(SungchibotException):
    """데이터베이스 오류"""
    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")


class AuthenticationError(SungchibotException):
    """인증 오류"""
    def __init__(self, message: str):
        super().__init__(message, "AUTHENTICATION_ERROR")


class NotFoundError(SungchibotException):
    """리소스를 찾을 수 없음"""
    def __init__(self, message: str):
        super().__init__(message, "NOT_FOUND_ERROR")


class ConfigurationError(SungchibotException):
    """설정 오류"""
    def __init__(self, message: str):
        super().__init__(message, "CONFIGURATION_ERROR")
