from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("services", "0004_search_indexes")]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="description",
            field=models.TextField(blank=True, max_length=2500),
        ),
        migrations.AlterField(
            model_name="category",
            name="description",
            field=models.TextField(blank=True, max_length=2500),
        ),
        migrations.AlterField(
            model_name="lending",
            name="notes",
            field=models.TextField(blank=True, max_length=2500),
        ),
    ]
