from datetime import datetime
from typing import Optional

from pydantic import validator

from app.models.base import TxtRowUDF


class OutreachCSV(object):
    def __init__(self):
        # TODO: Implement CSV Model
        pass


class Outreach(TxtRowUDF):
    rescheduled: int = 0
    cancelled: int = 0
    appointment_date: Optional[datetime] = None
    attempt_time: Optional[datetime] = None
    attempt_result: int
    unsuccessful: Optional[int]
    successful: Optional[int]

    @validator('unsuccessful')
    def validate_unsuccessful(cls, v):
        if cls.attempt_result == 2:
            if not v:
                raise ValueError('Unsuccessful is required')
            return v
        return None

    @validator('successful')
    def validate_successful(cls, v):
        if cls.attempt_result == 1:
            if not v:
                raise ValueError('Successful is required')
            return v
        return None
