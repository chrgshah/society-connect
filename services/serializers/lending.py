from rest_framework import serializers

from services.models.lending import Lending


class BorrowBookSerializer(serializers.Serializer):
    member_uuid = serializers.UUIDField()
    book_uuid = serializers.UUIDField()
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class ReturnBookSerializer(serializers.Serializer):
    pass


class LendingSerializer(serializers.ModelSerializer):
    member = serializers.SerializerMethodField()
    book = serializers.SerializerMethodField()

    class Meta:
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
        return {"uuid": str(obj.member.uuid), "full_name": obj.member.full_name}

    def get_book(self, obj):
        return {"uuid": str(obj.book.uuid), "title": obj.book.title}
