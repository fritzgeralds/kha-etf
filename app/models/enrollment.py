from datetime import datetime
from typing import Optional

from pydantic import validator

from app.models.base import TxtRowUDF


def get_role():
    # TODO - Implement get_role
    pass


def get_role_other(role):
    if role == 5:
        return 'Other'
    return None


class EnrollmentCSV(object):
    def __init__(self):
        # TODO: Implement CSV Model
        pass


class Enrollment(TxtRowUDF):
    next_visit: int = 0
    next_visit_date: Optional[datetime.date] = None
    role: int = 5
    role_other:  Optional[str] = None
    contact_date: datetime.date
    effective_date: datetime.date
    term_date: Optional[datetime.date] = None
    enrollment_flag: int = 1
    disenrollment_reason: Optional[str] =  None


    @validator('role_other')
    def validate_role_other(cls, v):
        if cls.role == 5:
            if not v:
                raise ValueError('Role Other is required')
            return v
        return None

    @validator('disenrollment_reason')
    def validate_disenrollment_reason(cls, v):
        if cls.enrollment_flag == 0:
            if not v:
                raise ValueError('Disenrollment Reason is required')
            return v
        return None
