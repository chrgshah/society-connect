"""Request and response serializers for lending workflows."""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from services.models.lending import Lending
from services.models.book import Book
from services.models.member import Member


class BorrowBookSerializer(serializers.Serializer):
    """Validate the identifiers and optional details needed to borrow a book."""

    member_uuid = serializers.UUIDField()
    book_uuid = serializers.UUIDField()
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=2000,
        trim_whitespace=True,
    )

    def validate_member_uuid(self, value):
        if not Member.objects.filter(uuid=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Member not found.")
        return value

    def validate_book_uuid(self, value):
        if not Book.objects.filter(uuid=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Book not found.")
        return value


class ReturnBookSerializer(serializers.Serializer):
    """Represent the currently body-less return request."""

    pass


class LendingSerializer(serializers.ModelSerializer):
    """Serialize lending history with nested member and book summaries."""

    member = serializers.SerializerMethodField()
    book = serializers.SerializerMethodField()

    class Meta:
        """Configure lending fields and nested summaries exposed by the API."""

        model = Lending
        fields = [
            "uuid",
            "member",
            "book",
            "borrowed_at",
            "due_at",
            "returned_at",
            "status",
            "notes",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.DictField)
    def get_member(self, obj):
        """Return compact member identity data for a lending."""
        return {"uuid": str(obj.member.uuid), "full_name": obj.member.full_name}

    @extend_schema_field(serializers.DictField)
    def get_book(self, obj):
        """Return compact book identity data for a lending."""
        return {"uuid": str(obj.book.uuid), "title": obj.book.title}
