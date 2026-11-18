from django.db import migrations


CORE_MOODS = [
    ("love", "In love", "♡"),
    ("sad", "Sad / hurt", "☂"),
    ("calm", "Calm", "◌"),
    ("focus", "Focused", "◎"),
    ("happy", "Happy", "☀"),
    ("energy", "Energized", "⚡"),
]


def seed_core_moods(apps, schema_editor):
    MoodTag = apps.get_model("music", "MoodTag")
    for slug, label, icon in CORE_MOODS:
        MoodTag.objects.update_or_create(
            slug=slug,
            defaults={"label": label, "icon": icon},
        )


def unseed_core_moods(apps, schema_editor):
    MoodTag = apps.get_model("music", "MoodTag")
    slugs = [slug for slug, _, _ in CORE_MOODS]
    MoodTag.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("music", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_core_moods, unseed_core_moods),
    ]
