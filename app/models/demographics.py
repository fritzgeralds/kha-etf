import json
import re
from typing import Optional, Dict

from pydantic import EmailStr, validator

from app.models.base import TxtRow


class Demographics(TxtRow):

    """
    This class is used to create a model for the demographics data.
    """
    dob: str
    gender: str
    last_name: str
    first_name: str
    middle_name: Optional[str]
    email: Optional[EmailStr]
    opt_txt: int = 0
    opt_call: int = 0
    phone: Optional[Dict[str]] = {'home': None, 'work': None, 'cell': None}
    address: Dict[str] = {
        'street': '601 24th St',
        'street2': '',
        'city': 'Bakersfield',
        'state': 'CA',
        'zip': '93301'
    }

    @validator('email')
    def validate_email(cls, v):
        if not re.fullmatch(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])", v):
            raise ValueError('Invalid Email')
        return v

    @validator('dob')
    def validate_dob(cls, v):
        if not v:
            raise ValueError('DOB is required')
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
            raise ValueError('Invalid DOB')
        return v

    def __str__(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return str(self)


class DemographicsCSV(object):
    def __init__(self, *args, **kwargs):
        # TODO: Implement CSV Model
        pass

    def write_good_row(self):
        row = f"{self.id}|{self.created}|{self.void}|{self.mem}|{self.cin}|" \
                   f"{self.dob}|{self.gender}|{self.last_name}|{self.first_name}|{self.middle}|" \
                   f"{self.email}|{self.phone['cell']}|{self.opt_txt}|{self.opt_call}|{self.phone['home']}|" \
                   f"{self.phone['work']}|{self.address['street']}|{self.address['street2']}|{self.address['city']}|" \
                   f"{self.address['state']}|{self.address['zip']}|{self.tin}|{self.npi}"
        return row

    def write_bad_row(self, reason):
        row = f"{self.id}|{self.created}|{self.void}|{self.mem}|{self.cin}|" \
                   f"{self.dob}|{self.gender}|{self.last_name}|{self.first_name}|{self.middle}|" \
                   f"{self.email}|{self.phone['cell']}|{self.opt_txt}|{self.opt_call}|{self.phone['home']}|" \
                   f"{self.phone['work']}|{self.address['street']}|{self.address['street2']}|{self.address['city']}|" \
                   f"{self.address['state']}|{self.address['zip']}|{self.tin}|{self.npi}|{reason}"
        return row

    def write_bad_row(self):
        #TODO: Implement Bad Row
        pass







a = DemographicsTXT(mem="abc123", cin="12345", dob="1/2/33", gender="M", last_name="Last Name", first_name="First Name", middle_name="Middle Name", email="e@mail.com", opt_call=1, home="5551234567", cell="5559876543", street="123 Street", city="Bakersfield", state="CA", zip="93301", tin="123456", npi="654321")
