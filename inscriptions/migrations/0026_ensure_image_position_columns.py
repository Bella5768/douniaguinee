from django.db import migrations


def _add_column_if_missing(schema_editor, table_name, column_name, sql_type_and_constraints):
    existing = [c.name for c in schema_editor.connection.introspection.get_table_description(schema_editor.connection.cursor(), table_name)]
    if column_name in existing:
        return
    schema_editor.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type_and_constraints}"
    )


def ensure_position_columns(apps, schema_editor):
    # Ensure the DB schema matches the current models even if a previous migration was faked.
    _add_column_if_missing(
        schema_editor,
        "inscriptions_evenementimage",
        "position",
        "varchar(20) NOT NULL DEFAULT 'galerie'",
    )
    _add_column_if_missing(
        schema_editor,
        "inscriptions_restitutionimage",
        "position",
        "varchar(20) NOT NULL DEFAULT 'galerie'",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("inscriptions", "0025_image_positions_for_hero"),
    ]

    operations = [
        migrations.RunPython(ensure_position_columns, migrations.RunPython.noop),
    ]
