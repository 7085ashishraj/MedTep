from rest_framework import serializers


class FacilityMatchSerializer(serializers.Serializer):
    """Only explicit public fields; dummy phone and action URLs are suppressed."""

    id = serializers.IntegerField(source="facility.pk")
    name = serializers.CharField(source="facility.name")
    facility_type = serializers.CharField(source="facility.facility_type")
    type_label = serializers.CharField(source="facility.get_facility_type_display")
    address = serializers.CharField(source="facility.address")
    latitude = serializers.FloatField(source="facility.latitude")
    longitude = serializers.FloatField(source="facility.longitude")
    specialities = serializers.SlugRelatedField(
        source="facility.specialities", many=True, read_only=True, slug_field="name",
    )
    is_24x7 = serializers.BooleanField(source="facility.is_24x7")
    is_demo = serializers.BooleanField(source="facility.is_demo")
    distance_km = serializers.FloatField(allow_null=True)
    phone = serializers.SerializerMethodField()
    call_url = serializers.CharField(allow_null=True)
    directions_url = serializers.CharField(allow_null=True)

    def get_phone(self, match):
        return None if match.facility.is_demo else match.facility.phone
