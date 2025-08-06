from cloe_metadata import base


def restore_old_databases(
    databases: base.Databases,
    databases_old: base.Databases,
) -> None:
    database_names = [database.name for database in databases.databases]
    for database in databases_old.databases:
        if database.name not in database_names:
            databases.databases.append(database)
