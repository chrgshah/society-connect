from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("services", "0002_book_author_text")]

    operations = [
        migrations.AddConstraint(
            model_name="book",
            constraint=models.CheckConstraint(
                check=models.Q(("total_copies__gt", 0)),
                name="book_total_copies_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="book",
            constraint=models.CheckConstraint(
                check=models.Q(("available_copies__lte", models.F("total_copies"))),
                name="book_available_not_above_total",
            ),
        ),
        migrations.AddConstraint(
            model_name="lending",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(("returned_at__isnull", False), ("status", "RETURNED"))
                    | models.Q(("returned_at__isnull", True), ("status__in", ["BORROWED", "OVERDUE"]))
                ),
                name="lending_return_state_consistent",
            ),
        ),
    ]
