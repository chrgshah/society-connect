"""Serialization schema for dashboard aggregate values."""

from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    """Describe the numeric counters returned by the dashboard endpoint."""

    total_books = serializers.IntegerField()
    total_copies = serializers.IntegerField()
    available_copies = serializers.IntegerField()
    borrowed_copies = serializers.IntegerField()
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    overdue_borrowings = serializers.IntegerField()
