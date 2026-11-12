from django.contrib import admin

from .models import Facility, Speciality


class DemoDataFilter(admin.SimpleListFilter):
    title = "data source"
    parameter_name = "demo"

    def lookups(self, request, model_admin):
        return (("yes", "FAKE sample data"), ("no", "Ordinary entries"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(demo_key__isnull=False)
        if self.value() == "no":
            return queryset.filter(demo_key__isnull=True)
        return queryset


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = (
        "name", "facility_type", "phone", "speciality_names", "is_24x7", "is_active", "demo_status",
    )
    list_filter = (
        "facility_type", "is_24x7", "is_active", DemoDataFilter,
        ("specialities", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = ("name", "address", "phone", "specialities__name")
    autocomplete_fields = ("specialities",)
    list_editable = ("is_24x7", "is_active")
    readonly_fields = ("demo_status", "demo_key", "created_at", "updated_at")
    list_per_page = 25
    ordering = ("name", "pk")
    fieldsets = (
        ("Facility details", {"fields": ("name", "facility_type", "specialities")}),
        ("Contact and location", {
            "fields": ("address", "phone", ("latitude", "longitude")),
            "description": "Use decimal degrees: latitude -90 to 90; longitude -180 to 180. Phone: 7–15 digits, optional +, no spaces.",
        }),
        ("Listing settings", {
            "fields": ("is_24x7", "is_active"),
            "description": "24x7 describes opening hours, not current beds or service availability. Active controls whether a record is eligible for later public listings.",
        }),
        ("Record information", {
            "fields": ("demo_status", "demo_key", "created_at", "updated_at"),
            "description": "FAKE sample locations and phone numbers are for learning only. Ordinary entries are not automatically verified.",
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("specialities")

    @admin.display(description="Specialities")
    def speciality_names(self, obj):
        return ", ".join(speciality.name for speciality in obj.specialities.all()) or "—"

    @admin.display(boolean=True, description="FAKE sample data")
    def demo_status(self, obj):
        return obj.is_demo
