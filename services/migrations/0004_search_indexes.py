from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("services", "0003_data_consistency_constraints")]

    operations = [
        migrations.AddIndex(
            model_name="book",
            index=models.Index(fields=["title"], name="book_title_idx"),
        ),
        migrations.AddIndex(
            model_name="book",
            index=models.Index(fields=["author"], name="book_author_idx"),
        ),
        migrations.AddIndex(
            model_name="book",
            index=models.Index(fields=["publisher"], name="book_publisher_idx"),
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["first_name"], name="member_first_name_idx"),
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["last_name"], name="member_last_name_idx"),
        ),
        migrations.AddIndex(
            model_name="member",
            index=models.Index(fields=["phone"], name="member_phone_idx"),
        ),
    ]
