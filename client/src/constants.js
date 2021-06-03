
const commonColumnMap = {
    'Vaccine': 'vaccine', 
    'Date': 'date',
    'Center Name': 'name',
    'Address': 'address',
    'Availability Dose1': 'available_capacity_dose1',
    'Availability Dose2': 'available_capacity_dose2',
    'Minimum Age': 'min_age_limit'
};
const commonColumns = ['Vaccine','Date','Center Name','Address',
    'Availability Dose1', 'Availability Dose2', 'Minimum Age'
];

export const districtColumnMap = {
    'District': 'district_name',
    'State': 'state_name',
    ...commonColumnMap
}
export const pincodeColumnMap = {
    'Pincode': 'pincode',
    ...commonColumnMap
}

export const disColumns = ['District', 'State', ...commonColumns];
export const pinColumns = ['Pincode', 'State', ...commonColumns];