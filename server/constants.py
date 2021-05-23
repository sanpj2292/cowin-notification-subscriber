from collections import OrderedDict

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