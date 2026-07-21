"""Serialization and validation for society members."""

from django.core.validators import RegexValidator
from rest_framework import serializers

from services.models.member import Member


class MemberSerializer(serializers.ModelSerializer):
    """Serialize members and enforce unique, normalized identity fields."""

    class Meta:
        """Configure member fields and generated values exposed by the API."""

        model = Member
        fields = [
            "uuid",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "membership_number",
            "membership_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]

    def validate_phone(self, value):
        """Normalize a phone number by trimming surrounding whitespace."""
        validator = RegexValidator(r"^\+?[0-9\s-]{7,}$")
        value = value.strip()
        validator(value)
        digits = "".join(character for character in value if character.isdigit())
        if not 7 <= len(digits) <= 15:
            raise serializers.ValidationError(
                "Enter a phone number with 7 to 15 digits."
            )
        return value

    def validate_email(self, value):
        """Normalize email and reject duplicates outside the current member."""
        value = value.strip().lower()
        if (
            Member.objects.filter(email__iexact=value, deleted_at__isnull=True)
            .exclude(pk=self.instance.pk if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError("Member with this email already exists.")
        return value

    def validate_membership_number(self, value):
        """Reject duplicate membership numbers outside the current member."""
        if (
            Member.objects.filter(membership_number=value, deleted_at__isnull=True)
            .exclude(pk=self.instance.pk if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError("Membership number already exists.")
        return value
