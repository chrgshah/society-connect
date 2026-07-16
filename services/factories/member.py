from django.db.models import Q
from services.models.member import Member


class MemberFactory:
    @staticmethod
    def create_member(data):
        membership_number = (
            data.get("membership_number") or MemberFactory._generate_membership_number()
        )
        return Member.objects.create(**{**data, "membership_number": membership_number})

    @staticmethod
    def update_member(member, data):
        for key, value in data.items():
            setattr(member, key, value)
        member.save()
        return member

    @staticmethod
    def deactivate_member(member):
        member.is_active = False
        member.save(update_fields=["is_active", "updated_at"])
        return member

    @staticmethod
    def get_queryset(search=None, is_active=None):
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
        last_member = (
            Member.objects.filter(deleted_at__isnull=True).order_by("-id").first()
        )
        next_id = (last_member.id if last_member else 0) + 1
        return f"MEM-{next_id:06d}"
