# etna:allowAlterField


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

# Tuple: (slug, name, year_from, year_to, available_for_resources)
TIME_PERIODS = [
    ("early-civilisations", "Early civilisations", None, 900, False),
    ("medieval", "Medieval", 900, 1485, True),
    ("early-modern", "Early modern", 1485, 1750, True),
    ("industrial-revolution", "Industrial revolution", 1750, 1901, True),
    ("early-twentieth-century", "Early Twentieth Century", 1901, 1945, True),
    ("post-war-and-modern", "Post-War and modern", 1945, None, True),
    ("cross-period", "Cross period", None, None, True),
]


def seed_key_stages(apps, schema_editor):
    KeyStage = apps.get_model("education", "KeyStage")
    key_stage_field_names = {field.name for field in KeyStage._meta.fields}

    for slug, name, stage, age_range in KEY_STAGES:
        defaults = {"name": name}
        defaults["stage"] = stage
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

    for slug, name, year_from, year_to, available_for_resources in TIME_PERIODS:
        defaults = {"name": name}

        if "year_from" in time_period_field_names:
            defaults["year_from"] = year_from

        if "year_to" in time_period_field_names:
            defaults["year_to"] = year_to

        if "available_for_resources" in time_period_field_names:
            defaults["available_for_resources"] = available_for_resources

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
