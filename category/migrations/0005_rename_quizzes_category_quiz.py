from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0004_category_image_category_transparent'),
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='quizzes',
            new_name='quiz',
        ),
    ]
