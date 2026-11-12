"""Entirely fictional facilities. These are not healthcare recommendations."""

from decimal import Decimal

from .models import Facility

DEMO_SPECIALITIES = {
    "general-medicine": "General medicine",
    "emergency-care": "Emergency care",
    "cardiology": "Cardiology",
    "paediatrics": "Paediatrics",
    "pharmacy-services": "Pharmacy services",
    "blood-services": "Blood services",
}

# Synthetic positions in one cluster for later distance-search practice.
# They are not the positions of actual facilities. Never call the dummy number.
DEMO_FACILITIES = (
    {
        "key": "medtap-demo-hospital-alpha", "name": "FAKE Demo Hospital Alpha",
        "type": Facility.Type.HOSPITAL, "latitude": "12.970000", "longitude": "77.590000",
        "specialities": ("general-medicine", "emergency-care", "cardiology"),
        "is_24x7": True, "is_active": True,
    },
    {
        "key": "medtap-demo-hospital-beta", "name": "FAKE Demo Hospital Beta",
        "type": Facility.Type.HOSPITAL, "latitude": "12.980000", "longitude": "77.600000",
        "specialities": ("general-medicine", "paediatrics"),
        "is_24x7": False, "is_active": True,
    },
    {
        "key": "medtap-demo-clinic-alpha", "name": "FAKE Demo Clinic Alpha",
        "type": Facility.Type.CLINIC, "latitude": "12.975000", "longitude": "77.585000",
        "specialities": ("general-medicine",), "is_24x7": False, "is_active": True,
    },
    {
        "key": "medtap-demo-clinic-beta", "name": "FAKE Demo Clinic Beta",
        "type": Facility.Type.CLINIC, "latitude": "12.960000", "longitude": "77.605000",
        "specialities": ("paediatrics",), "is_24x7": False, "is_active": True,
    },
    {
        "key": "medtap-demo-pharmacy-alpha", "name": "FAKE Demo Pharmacy Alpha",
        "type": Facility.Type.PHARMACY, "latitude": "12.968000", "longitude": "77.595000",
        "specialities": ("pharmacy-services",), "is_24x7": True, "is_active": True,
    },
    {
        "key": "medtap-demo-pharmacy-beta", "name": "FAKE Demo Pharmacy Beta",
        "type": Facility.Type.PHARMACY, "latitude": "12.990000", "longitude": "77.610000",
        "specialities": ("pharmacy-services",), "is_24x7": False, "is_active": False,
    },
    {
        "key": "medtap-demo-blood-bank-alpha", "name": "FAKE Demo Blood Bank Alpha",
        "type": Facility.Type.BLOOD_BANK, "latitude": "12.965000", "longitude": "77.580000",
        "specialities": ("blood-services",), "is_24x7": True, "is_active": True,
    },
    {
        "key": "medtap-demo-blood-bank-beta", "name": "FAKE Demo Blood Bank Beta",
        "type": Facility.Type.BLOOD_BANK, "latitude": "12.985000", "longitude": "77.575000",
        "specialities": ("blood-services",), "is_24x7": False, "is_active": True,
    },
)


def facility_defaults(sample, position):
    return {
        "name": sample["name"],
        "facility_type": sample["type"],
        "address": f"FAKE address {position}, Example Road, Demo District. No real facility exists here.",
        "phone": "0000000000",
        "latitude": Decimal(sample["latitude"]),
        "longitude": Decimal(sample["longitude"]),
        "is_24x7": sample["is_24x7"],
        "is_active": sample["is_active"],
    }
