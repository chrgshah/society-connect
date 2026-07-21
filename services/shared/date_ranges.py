"""Shared validation for bounded reporting date ranges."""

import calendar
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers


def six_months_before(value):
    """Return the same calendar day six months earlier, clamped by month length."""
    month_index = value.year * 12 + value.month - 1 - 6
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def validate_date_range(from_date=None, to_date=None):
    """Default to seven days and enforce an ordered, non-future six-month range."""
    today = timezone.localdate()
    to_date = to_date or today
    from_date = from_date or to_date - timedelta(days=6)
    if from_date > to_date:
        raise serializers.ValidationError(
            {"from_date": "From date must be on or before to date."}
        )
    if to_date > today:
        raise serializers.ValidationError({"to_date": "Future dates are not allowed."})
    if from_date < six_months_before(to_date):
        raise serializers.ValidationError(
            {"from_date": "Date range cannot exceed six months."}
        )
    return from_date, to_date
