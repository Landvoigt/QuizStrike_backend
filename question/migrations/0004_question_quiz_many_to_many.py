import django.db.models.deletion
from django.db import migrations, models


def copy_foreign_key_to_many_to_many(apps, schema_editor):
    Question = apps.get_model("question", "Question")
    Through = Question.quiz_many.through
    Through.objects.bulk_create(
        Through(question_id=question_id, quiz_id=quiz_id)
        for question_id, quiz_id in Question.objects.values_list("id", "quiz_id")
    )


def copy_many_to_many_to_foreign_key(apps, schema_editor):
    Question = apps.get_model("question", "Question")
    Through = Question.quiz_many.through
    for question in Question.objects.all():
        link = Through.objects.filter(question_id=question.id).order_by("id").first()
        if link is None:
            raise RuntimeError(f"Question {question.id} has no quiz, cannot migrate backwards.")
        Question.objects.filter(pk=question.pk).update(quiz_id=link.quiz_id)


class Migration(migrations.Migration):

    dependencies = [
        ('question', '0003_alter_question_category_alter_question_quiz'),
        ('quiz', '0001_initial'),
    ]

    # The many-to-many field is added under a temporary name and without a reverse
    # name, because the old foreign key still owns "quiz" and quiz.questions.
    operations = [
        migrations.AddField(
            model_name='question',
            name='quiz_many',
            field=models.ManyToManyField(related_name='+', to='quiz.quiz'),
        ),
        migrations.AlterField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quiz.quiz'),
        ),
        migrations.RunPython(copy_foreign_key_to_many_to_many, copy_many_to_many_to_foreign_key),
        migrations.RemoveField(
            model_name='question',
            name='quiz',
        ),
        migrations.RenameField(
            model_name='question',
            old_name='quiz_many',
            new_name='quiz',
        ),
        migrations.AlterField(
            model_name='question',
            name='quiz',
            field=models.ManyToManyField(related_name='questions', to='quiz.quiz'),
        ),
    ]
