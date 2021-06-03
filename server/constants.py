from collections import OrderedDict
import os

BASE_URL = 'https://cdn-api.co-vin.in/api/v2/appointment'
LOC_BASE_URL = 'https://cdn-api.co-vin.in/api/v2/admin/location'
headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'
}
DISTRICT_ID = 581 #Hyderabad

emailCommonColumns = [
    ('Vaccine', 'vaccine'), 
    ('Date', 'date'),
    ('Center Name', 'name'),
    ('Address', 'address'),
    ('Availability Dose1', 'available_capacity_dose1'),
    ('Availability Dose2', 'available_capacity_dose2'),
    ('Minimum Age', 'min_age_limit'),
]
emailDistrictColumns = OrderedDict([
    ('District', 'state_name'), 
    ('State', 'district_name'), 
    *emailCommonColumns,
])

emailPincodeColumns = OrderedDict([
    ('Pincode', 'pincode'), 
    *emailCommonColumns,
])


DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(os.getcwd(),"../secrets/private_key.txt")
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(os.getcwd(),"../secrets/public_key.txt")

VAPID_PRIVATE_KEY = open(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, "r+").readline().strip("\n")
VAPID_PUBLIC_KEY = open(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, "r+").read().strip("\n")

VAPID_CLAIMS = {
    "sub": "mailto:mailer.cowin@gmail.com"
}