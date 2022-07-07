import json
from typing import Optional

from pydantic import validator

from app.models.base import TxtRowUDF
from app.models.error import Error

import logging
logger = logging.getLogger(__name__.split('.')[-1])


class Outreach(TxtRowUDF):
    rescheduled: int = 0
    cancelled: int = 0
    appointment_date: Optional[str]
    attempt_time: Optional[str]
    attempt_result: int = 0
    unsuccessful: Optional[int]
    successful: Optional[int]

    class Config:
        validate_assignment = True

    @validator('unsuccessful')
    def validate_unsuccessful(cls, v, values):
        if values['attempt_result'] == 2:
            if not v:
                raise Error(message=f"{values['filename']} :: Row: {values['row_id']} - Unsuccessful is required")
            return v
        return None

    @validator('successful')
    def validate_successful(cls, v, values):
        if values['attempt_result'] == 1:
            if not v:
                raise Error(message=f"{values['filename']} :: Row: {values['row_id']} - Successful is required")
            return v
        return None

    def write_row(self):
        row = f"{self.id}|{self.date}|{self.void}|{self.mem_id}|{self.cin}|{self.rescheduled}|" \
                   f"{self.cancelled}|{self.appointment_date}|{self.attempt_time}|{self.attempt_result}|" \
                   f"{self.unsuccessful}|{self.successful}|{self.tin}|{self.npi}|{self.program}"
        for i in range(len(self.udf)):
            row += f"|{self.udf[i][f'udf_{i + 1}']['code']}|{self.udf[i][f'udf_{i + 1}']['desc']}"
        return row.replace('None', '')

    def __str__(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return str(self)
