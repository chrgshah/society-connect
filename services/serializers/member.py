from django.core.validators import RegexValidator
from rest_framework import serializers

from services.models.member import Member


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
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
        validator = RegexValidator(r"^\+?[0-9\s-]{7,}$")
        validator(value)
        return value

    def validate_email(self, value):
        if (
            Member.objects.filter(email=value, deleted_at__isnull=True)
            .exclude(pk=self.instance.pk if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError("Member with this email already exists.")
        return value

    def validate_membership_number(self, value):
        if (
            Member.objects.filter(membership_number=value, deleted_at__isnull=True)
            .exclude(pk=self.instance.pk if self.instance else None)
            .exists()
        ):
            raise serializers.ValidationError("Membership number already exists.")
        return value
