from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from services.models.author import Author
from services.models.book import Book
from services.models.category import Category
from services.models.lending import Lending
from services.models.member import Member
from services.models.user import User


class Command(BaseCommand):
    help = "Seed sample library data"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com"},
        )
        if created or not user.password or user.password == "!":
            user.set_password("Admin@12345")
            user.save(update_fields=["password"])

        author_names = ["Jane Austen", "George Orwell", "Haruki Murakami", "Agatha Christie"]
        authors = []
        for name in author_names:
            author, _ = Author.objects.get_or_create(name=name)
            authors.append(author)

        category_names = ["Fiction", "Science", "History", "Mystery"]
        categories = []
        for name in category_names:
            category, _ = Category.objects.get_or_create(name=name)
            categories.append(category)

        for idx, author in enumerate(authors, start=1):
            category = categories[(idx - 1) % len(categories)]
            Book.objects.get_or_create(
                isbn=f"978000000000{idx}",
                defaults={
                    "title": f"Sample Book {idx}",
                    "author": author,
                    "category": category,
                    "publisher": "Example Press",
                    "published_year": 2020 + idx,
                    "description": "Seeded demo book",
                    "total_copies": 2,
                    "available_copies": 2,
                    "shelf_location": f"Shelf {idx}",
                },
            )

        for idx in range(1, 6):
            Member.objects.get_or_create(
                email=f"member{idx}@example.com",
                defaults={
                    "first_name": f"Member{idx}",
                    "last_name": "Test",
                    "phone": f"+1234567890{idx}",
                    "address": "Example Street",
                    "membership_number": f"MEM-{idx:06d}",
                    "membership_date": "2024-01-01",
                    "is_active": True,
                },
            )

        sample_book = Book.objects.order_by("id").first()
        sample_member = Member.objects.order_by("id").first()
        if sample_book and sample_member and not Lending.objects.exists():
            Lending.objects.create(member=sample_member, book=sample_book, due_at=timezone.now() + timedelta(days=7), notes="Sample")

        self.stdout.write(self.style.SUCCESS("Seed data created."))
