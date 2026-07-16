from django.db import migrations, models


def copy_author_names(apps, schema_editor):
    Book = apps.get_model("services", "Book")
    for book in Book.objects.select_related("author").all():
        book.author_name = book.author.name
        book.save(update_fields=["author_name"])


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="author_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.RunPython(copy_author_names, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="book",
            name="author",
        ),
        migrations.RenameField(
            model_name="book",
            old_name="author_name",
            new_name="author",
        ),
        migrations.AlterField(
            model_name="book",
            name="author",
            field=models.CharField(max_length=200),
        ),
        migrations.DeleteModel(
            name="Author",
        ),
    ]
