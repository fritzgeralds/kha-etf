import json
from typing import Optional

from pydantic import validator

from app.models.base import TxtRowUDF
from app.models.error import Error

import logging
logger = logging.getLogger(__name__.split('.')[-1])


def get_role_other(role):
    if role == 5:
        return 'Other'
    return None


class Enrollment(TxtRowUDF):
    next_visit: int = 0
    next_visit_date: Optional[str] = ''
    role: int = 5
    role_other:  Optional[str] = ''
    contact_date: str
    effective_date: str
    term_date: Optional[str] = ''
    enrollment_flag: int = 1
    disenrollment_reason: Optional[str] = ''

    class Config:
        validate_assignment = True

    @validator('role_other')
    def validate_role_other(cls, v, values):
        if values['role'] == 5:
            if not v:
                raise Error(message=f"{values['filename']} :: Row: {values['row_id']} - Role Other is required")
            return v
        return None

    @validator('disenrollment_reason')
    def validate_disenrollment_reason(cls, v, values):
        if values['enrollment_flag'] == 0:
            if not v:
                raise Error(message=f"{values['filename']} :: Row: {values['row_id']} - Disenrollment Reason is required")
            return v
        return None

    def write_row(self):
        row = f"{self.id}|{self.date}|{self.void}|{self.mem_id}|{self.cin}|" \
              f"{self.next_visit}|{self.next_visit_date}|{self.role}|{self.role_other}|{self.contact_date}|" \
              f"{self.effective_date}|{self.term_date}|{self.enrollment_flag}|{self.disenrollment_reason}|" \
              f"{self.tin}|{self.npi}|{self.program}"
        for i in range(len(self.udf)):
            row += f"|{self.udf[i][f'udf_{i + 1}']['code']}|{self.udf[i][f'udf_{i + 1}']['desc']}"
        return row.replace('None', '')

    def __str__(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return str(self)
