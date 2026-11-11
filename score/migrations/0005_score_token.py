from django.db import migrations, models

from score.models import generate_token


def fill_tokens(apps, schema_editor):
    Score = apps.get_model("score", "Score")
    for pk in Score.objects.filter(token__isnull=True).values_list("pk", flat=True):
        Score.objects.filter(pk=pk).update(token=generate_token())


class Migration(migrations.Migration):

    dependencies = [
        ('score', '0004_score_time_only_correct'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='token',
            field=models.CharField(max_length=64, null=True, editable=False),
        ),
        migrations.RunPython(fill_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='score',
            name='token',
            field=models.CharField(default=generate_token, editable=False, max_length=64, unique=True),
        ),
    ]
