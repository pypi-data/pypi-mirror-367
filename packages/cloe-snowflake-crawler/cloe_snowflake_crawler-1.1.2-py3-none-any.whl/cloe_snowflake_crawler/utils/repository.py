from cloe_metadata import base


def merge_repository_content(
    new_content: base.Databases,
    old_content: base.Databases,
) -> base.Databases:
    old_databases = {f"{database.name}": database for database in old_content.databases}
    old_schemas = {
        f"{database.name}.{schema.name}": schema
        for database in old_content.databases
        for schema in database.schemas
    }
    old_tables = {
        f"{database.name}.{schema.name}.{table.name}": table
        for database in old_content.databases
        for schema in database.schemas
        for table in schema.tables
    }
    for database in new_content.databases:
        if old_database := old_databases.get(
            f"{database.name}",
        ):
            database.id = old_database.id
            database.display_name = old_database.display_name
        for schema in database.schemas:
            if old_schema := old_schemas.get(
                f"{database.name}.{schema.name}",
            ):
                schema.id = old_schema.id
            for table in schema.tables:
                if old_table := old_tables.get(
                    f"{database.name}.{schema.name}.{table.name}",
                ):
                    table.id = old_table.id
                    table.level = old_table.level
    return new_content
