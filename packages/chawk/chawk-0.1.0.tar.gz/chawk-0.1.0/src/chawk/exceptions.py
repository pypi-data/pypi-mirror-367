class BlackboardAPIError(Exception):
    """Base exception for all Blackboard API errors."""

class BbPyAPIError(Exception):
    """Generic exception for all Bbpy errors."""

class AuthenticationError(BlackboardAPIError):
    """Raised when authentication fails or token is invalid."""

class UserNotFoundError(BlackboardAPIError):
    """Raised when a requested user does not exist."""

class CourseNotFoundError(BlackboardAPIError):
    """Raised when a requested course does not exist."""

class GradebookColumnNotFoundError(BlackboardAPIError):
    """Raised when a requested gradebook column does not exist."""

class RateLimitExceeded(BlackboardAPIError):
    """Raised when API rate limit is exceeded."""

class InvalidRequestError(BlackboardAPIError):
    """Raised when a request is badly formatted or missing parameters."""

class ServerError(BlackboardAPIError):
    """Raised when Blackboard returns a 5xx server error."""

class UserAlreadyExistsError(BlackboardAPIError):
    """Raised when user is already in the system."""


class UserCreationFailedError(BlackboardAPIError):
    """Raised when creating a user fails."""