"""Domain operations and query construction for members."""

from django.db.models import Q
from services.models.member import Member


class MemberFactory:
    """Create, update, deactivate, and query member records."""

    @staticmethod
    def create_member(data):
        """Create a member, generating a membership number when omitted."""
        membership_number = (
            data.get("membership_number") or MemberFactory._generate_membership_number()
        )
        return Member.objects.create(**{**data, "membership_number": membership_number})

    @staticmethod
    def update_member(member, data):
        """Apply validated fields to an existing member."""
        for key, value in data.items():
            setattr(member, key, value)
        member.save()
        return member

    @staticmethod
    def deactivate_member(member):
        """Mark a member inactive without deleting historical data."""
        member.is_active = False
        member.save(update_fields=["is_active", "updated_at"])
        return member

    @staticmethod
    def get_queryset(search=None, is_active=None):
        """Build a member queryset from optional text and status filters."""
        queryset = Member.objects.filter(deleted_at__isnull=True)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(membership_number__icontains=search)
            )
        if is_active is not None:
            active_value = str(is_active).lower() in {"true", "1", "yes"}
            queryset = queryset.filter(is_active=active_value)
        return queryset

    @staticmethod
    def _generate_membership_number():
        """Generate the next human-readable membership number."""
        last_member = (
            Member.objects.filter(deleted_at__isnull=True).order_by("-id").first()
        )
        next_id = (last_member.id if last_member else 0) + 1
        return f"MEM-{next_id:06d}"
