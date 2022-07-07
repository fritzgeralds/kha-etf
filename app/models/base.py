import re
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, validator
from app.models.error import Error

import logging
logger = logging.getLogger(__name__.split('.')[-1])


class TxtRow(BaseModel):
    filename: str
    row_id: int
    id: str
    date: str = datetime.strftime(datetime.now(), '%m-%d-%Y %H:%M:%S')
    void: int = 0
    mem_id: str
    cin: str
    tin: str = '956001629'
    npi: int = 1437825213
    program: str = 'CSS'

    @validator('mem_id')
    def validate_mem_id(cls, v, values):
        if not v:
            raise Error(message=f"{values['filename']} :: Row: {values['row_id']} - Member ID is required")
        if len(v) != 10 or re.fullmatch(r'^MEM(\d)\1+$', v.upper()):
            raise Error(message=f"{values['filename']} :: Row: {values['row_id']} - Invalid Member ID")
        return v

    @validator('cin')
    def validate_cin(cls, v, values):
        if not v:
            raise ValueError('CIN is required')
        if (len(v) != 9
                or not re.fullmatch(r"^9(\d{7})[A-Z]$", v.upper())
                or re.fullmatch(r"^9(\d)\1+[A-Z]$", v.upper())):
            raise Error(message=f"{values['filename']} :: Row: {values['row_id']} - Invalid CIN")
        return v


class TxtRowUDF(TxtRow):
    udf: Optional[List[dict]] = []

    @validator('udf')
    def validate_udf(cls, v, values):
        bad_udf = []
        if not v:
            raise ValueError('UDF is required')
        for i in range(len(v)):
            if v[i][f'udf_{i + 1}']['code'] and not v[i][f'udf_{i + 1}']['desc']:
                bad_udf.append("UDF %d has code but no description" % (i + 1))
            if not v[i][f'udf_{i + 1}']['code'] and v[i][f'udf_{i + 1}']['desc']:
                bad_udf.append("UDF %d has description but no code" % (i + 1))
        if bad_udf:
            raise Error(message=f"{values['filename']} :: Row: {values['row_id']} - " + ', '.join(bad_udf))
        return v
