"""Request and response serializers for lending workflows."""

from rest_framework import serializers

from services.models.lending import Lending


class BorrowBookSerializer(serializers.Serializer):
    """Validate the identifiers and optional details needed to borrow a book."""

    member_uuid = serializers.UUIDField()
    book_uuid = serializers.UUIDField()
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


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

    def get_member(self, obj):
        """Return compact member identity data for a lending."""
        return {"uuid": str(obj.member.uuid), "full_name": obj.member.full_name}

    def get_book(self, obj):
        """Return compact book identity data for a lending."""
        return {"uuid": str(obj.book.uuid), "title": obj.book.title}
