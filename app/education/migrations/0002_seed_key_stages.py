# etna:allowAlterField

from datetime import date

from django.db import migrations

KEY_STAGES = [
    ("key-stage-1", "Key stage 1", 1, "5-7"),
    ("key-stage-2", "Key stage 2", 2, "7-11"),
    ("key-stage-3", "Key stage 3", 3, "11-14"),
    ("key-stage-4", "Key stage 4", 4, "14-16"),
    ("key-stage-5", "Key stage 5", 5, "16-18"),
]

THEMES = [
    ("power-politics-and-reform", "Power, politics and reform"),
    ("war-and-revolution", "War and revolution"),
    ("migration-and-identity", "Migration and identity"),
    ("empire-and-decolonisation", "Empire and decolonisation"),
    ("crime-and-punishment", "Crime and punishment"),
    ("medicine-welfare-and-society", "Medicine, welfare and society"),
    ("family-community-and-everyday-life", "Family, community and everyday life"),
    ("economy-trade-and-industry", "Economy, trade and industry"),
    ("archive-skills", "Archive skills"),
    ("local-history", "Local history"),
    ("womens-history", "Women's history"),
    ("black-asian-and-global-majority-history", "Black, Asian and global majority history"),
    ("lgbtq-history", "LGBTQ+ history"),
    ("disability-history", "Disability history"),
    ("significant-people-places-and-events", "Significant people, places and events"),
]

TIME_PERIODS = [
    ("early-civilisations-pre-900", "Early civilisations (pre 900)", None, date(900, 1, 1)),
    ("medieval-900-1485", "Medieval (900-1485)", date(900, 1, 1), date(1485, 12, 31)),
    ("early-modern-1485-1750", "Early modern (1485-1750)", date(1485, 1, 1), date(1750, 12, 31)),
    ("industrial-revolution-1750-1901", "Industrial revolution (1750-1901)", date(1750, 1, 1), date(1901, 12, 31)),
    ("early-twentieth-century-1901-1945", "Early Twentieth Century (1901-1945)", date(1901, 1, 1), date(1945, 12, 31)),
    ("post-war-and-modern-1945-present", "Post-War and modern (1945- present)", date(1945, 1, 1), None),
    ("cross-period", "Cross period", None, None),
]


def seed_key_stages(apps, schema_editor):
    KeyStage = apps.get_model("education", "KeyStage")
    key_stage_field_names = {field.name for field in KeyStage._meta.fields}

    for slug, name, stage, age_range in KEY_STAGES:
        defaults = {"name": name}

        if "stage" in key_stage_field_names:
            defaults["stage"] = stage

        if "age_range" in key_stage_field_names:
            defaults["age_range"] = age_range

        KeyStage.objects.update_or_create(
            slug=slug,
            defaults=defaults,
        )


def seed_themes(apps, schema_editor):
    Theme = apps.get_model("education", "Theme")

    for slug, name in THEMES:
        Theme.objects.update_or_create(
            slug=slug,
            defaults={"name": name},
        )


def seed_time_periods(apps, schema_editor):
    TimePeriod = apps.get_model("education", "TimePeriod")
    time_period_field_names = {field.name for field in TimePeriod._meta.fields}

    for slug, name, date_from, date_to in TIME_PERIODS:
        defaults = {"name": name}

        if "date_from" in time_period_field_names:
            defaults["date_from"] = date_from

        if "date_to" in time_period_field_names:
            defaults["date_to"] = date_to

        TimePeriod.objects.update_or_create(
            slug=slug,
            defaults=defaults,
        )


def seed_education_taxonomies(apps, schema_editor):
    seed_key_stages(apps, schema_editor)
    seed_themes(apps, schema_editor)
    seed_time_periods(apps, schema_editor)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("education", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_education_taxonomies, noop_reverse),
    ]