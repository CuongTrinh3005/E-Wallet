import enum


class StatusEnum(enum.Enum):
    Initialized = "initialized"
    Confirmed = "confirmed"
    Verified = "verified"
    Completed = "completed"
    Expired = "expired"
    Canceled = "canceled"
    Failed = "failed"