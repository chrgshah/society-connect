"""Serialization schema for dashboard aggregate values."""

from rest_framework import serializers

from services.shared.date_ranges import validate_date_range


class DashboardDateRangeSerializer(serializers.Serializer):
    """Validate optional dashboard reporting boundaries."""

    from_date = serializers.DateField(required=False)
    to_date = serializers.DateField(required=False)

    def validate(self, attrs):
        from_date, to_date = validate_date_range(
            attrs.get("from_date"), attrs.get("to_date")
        )
        return {"from_date": from_date, "to_date": to_date}


class DashboardSummarySerializer(serializers.Serializer):
    """Describe the numeric counters returned by the dashboard endpoint."""

    total_books = serializers.IntegerField()
    total_copies = serializers.IntegerField()
    available_copies = serializers.IntegerField()
    borrowed_copies = serializers.IntegerField()
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    overdue_borrowings = serializers.IntegerField()
