import logging
import pathlib
from typing import Annotated, Optional

import typer
from cloe_metadata import base
from cloe_util_snowflake_connector import connection_parameters
from snowflake.connector import connect
from snowflake.core import Root

from cloe_snowflake_crawler import utils
from cloe_snowflake_crawler.crawler import snowflake_crawler

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def crawl(
    output_json_path: Annotated[
        pathlib.Path,
        typer.Argument(help="Path to save the crawled output to."),
    ],
    ignore_columns: Annotated[
        bool,
        typer.Option(
            help="Ignore columns of tables and just retrieve information about the table itself.",
        ),
    ] = False,
    ignore_tables: Annotated[
        bool,
        typer.Option(
            help="Ignore tables and just retrieve information about the higher level objects.",
        ),
    ] = False,
    existing_model_path: Annotated[
        Optional[pathlib.Path],  # noqa: UP007
        typer.Option(help="Will look for an existing model in path and update it."),
    ] = None,
    database_filter: Annotated[
        Optional[str],  # noqa: UP007
        typer.Option(
            help="Filters databases based on defined filter. Is used as Snowflake wildcard pattern in SHOW DATABASES. If no filter defined all databases are retrieved.",
        ),
    ] = None,
    database_name_replace: Annotated[
        Optional[str],  # noqa: UP007
        typer.Option(
            help="Replaces parts of a name with the CLOE env placeholder. Can be regex. Can be used to remove the environment part in a database name.",
        ),
    ] = None,
    delete_old_databases: Annotated[
        bool,
        typer.Option(help="Delete old databases if do not exist in target."),
    ] = False,
    include_only_base_tables: Annotated[
        bool,
        typer.Option(help="Restrict the crawler to include only base tables in the schema"),
    ] = True,
) -> None:
    """
    Crawls a snowflake instance and writes all
    metadata about database entities in a CLOE Repository JSON.
    """
    conn_params = connection_parameters.ConnectionParameters.init_from_env_variables()
    connection = connect(**conn_params.model_dump())
    root = Root(connection)

    crawler = snowflake_crawler.SnowflakeCrawler(
        snf_root=root,
        ignore_tables=ignore_tables,
        ignore_columns=ignore_columns,
        database_filter=database_filter,
        database_name_replace=database_name_replace,
        include_only_base_tables=include_only_base_tables,
    )
    crawler.crawl()
    connection.close()
    databases = crawler.databases
    if existing_model_path is not None:
        databases_old, errors = base.Databases.read_instances_from_disk(
            existing_model_path,
        )
        if len(errors) > 0:
            raise ValueError(
                "The provided models did not pass validation, please run validation.",
            )
        databases = utils.merge_repository_content(databases, databases_old)
        if delete_old_databases is False:
            utils.restore_old_databases(databases=databases, databases_old=databases)
    databases.write_to_disk(output_path=output_json_path, delete_existing=True)
