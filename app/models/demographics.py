import json
import re
from typing import Optional

from pydantic import validator

from app.models.base import TxtRow
from app.models.error import Error


class Demographics(TxtRow):

    """
    This class is used to create a model for the demographics data.
    """
    dob: str
    gender: str
    last_name: str
    first_name: str
    middle_name: Optional[str]
    email: Optional[str] = None
    opt_txt: int
    opt_call: int
    phone: Optional[dict] = {'home': None, 'work': None, 'cell': None}
    address: Optional[dict] = {'street': None, 'street2': None, 'city': None, 'state': None, 'zip': None}

    class Config:
        validate_assignment = True

    @validator('email')
    def validate_email(cls, v):
        if v:
            if not re.fullmatch(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])", v):
                raise Error(message='Invalid Email')
        return v

    @validator('address')
    def validate_address(cls, v, values):
        if any(v.values()):
            for key, value in v.items():
                if key != 'street2' and not value:
                    raise Error(message='Row: {} - Invalid Address: {} is required'.format(values['row_id'], key.title()))
        address = [v['street'], v['city'], v['state'], v['zip']]
        if not all(address):
            return {'street': '601 24th St', 'street2': '', 'city': 'Bakersfield', 'state': 'CA', 'zip': '93301'}
        return v

    @validator('dob')
    def validate_dob(cls, v):
        if not v:
            raise Error(message='DOB is required')
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', v):
            raise Error(message='Invalid DOB')
        return v

    def write_row(self):
        row = f"{self.id}|{self.date}|{self.void}|{self.mem_id}|{self.cin}|" \
                   f"{self.dob}|{self.gender}|{self.last_name}|{self.first_name}|{self.middle_name}|" \
                   f"{self.email}|{self.phone['cell']}|{self.opt_txt}|{self.opt_call}|{self.phone['home']}|" \
                   f"{self.phone['work']}|{self.address['street']}|{self.address['street2']}|{self.address['city']}|" \
                   f"{self.address['state']}|{self.address['zip']}|{self.tin}|{self.npi}"
        return row.replace('None', '')

    def __str__(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return str(self)
