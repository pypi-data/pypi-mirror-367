import logging
import re
import uuid
from dataclasses import dataclass

import cloe_metadata.base.repository.database.column as base_column
import jinja2 as j2
from cloe_metadata import base
from pydantic import BaseModel, ConfigDict
from snowflake.core import Root
from snowflake.core.table import TableColumn

from ..utils.template_env import env_sql

logger = logging.getLogger(__name__)


@dataclass
class Sqltype:
    type_name: str
    length: int | None = None
    precision: int | None = None
    scale: int | None = None


def extract_sql_type_info(data_type_str):
    # Regular expression to match the pattern
    pattern = r"(?P<type>[A-Z_]+)(?:\((?P<length>\d+)(?:, *(?P<scale>\d+))?\))?"
    match = re.match(pattern, data_type_str.strip().upper())

    if not match:
        return Sqltype(type_name=data_type_str)

    # Extracting the groups from the match
    sql_type = match.group("type")
    length = match.group("length")
    scale = match.group("scale")

    # Converting to integers if they are not None
    length = int(length) if length else None
    scale = int(scale) if scale else None

    # Depending on the type, return the appropriate tuple
    if sql_type in ["VARCHAR", "CHAR", "CHARACTER", "STRING", "TEXT"]:
        return Sqltype(type_name=sql_type, length=length)
    elif sql_type in ["NUMBER", "NUMERIC", "DECIMAL"]:
        return Sqltype(type_name=sql_type, precision=length, scale=scale)
    elif sql_type in ["FLOAT", "DOUBLE", "REAL"]:
        return Sqltype(type_name=sql_type)
    else:
        return Sqltype(type_name=sql_type)


class SnowflakeCrawler(BaseModel):
    """
    Class to construct a crawler to retrieve snowflake metadata
    and transform to a CLOE compatible format.
    """

    snf_root: Root
    ignore_columns: bool
    ignore_tables: bool
    databases: base.Databases = base.Databases(databases=[])
    schemas: dict[str, list[base.Schema]] = {}
    databases_cache: dict[str, base.Database] = {}
    templates_env: j2.Environment = env_sql
    database_filter: str | None = None
    database_name_replace: str | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True)
    include_only_base_tables: bool = True

    def _get_databases(self) -> None:
        """Retrieves databases in snowflake and adds them to the repository."""
        pattern = re.compile(self.database_filter) if self.database_filter is not None else None
        filtered_databases = [
            d.name
            for d in self.snf_root.databases.iter()
            if (pattern is None or pattern.match(d.name) is not None)
            and d.name.lower() not in ("snowflake", "snowflake_sample_data")
        ]
        for db_name in filtered_databases:
            database = base.Database(display_name=db_name, name=db_name, schemas=[])
            self.databases_cache[database.name] = database
            self.databases.databases.append(database)

    def _transform_table_columns(
        self,
        table_columns: list[TableColumn] | None,
    ) -> list[base_column.Column]:
        """
        Transforms a query result from a snowflake information schema
        columns view into a CLOE columns object and gathering all columns
        of all table in a dict.
        """
        columns: list[base_column.Column] = []
        for index, col in enumerate(table_columns or [], start=1):
            sqltype = extract_sql_type_info(col.datatype)
            column = base_column.Column(
                name=col.name,
                ordinal_position=index,
                is_key=col.autoincrement,
                is_nullable=col.nullable,
                data_type=sqltype.type_name,
                constraints=col.default,
                data_type_length=sqltype.length,
                data_type_numeric_scale=sqltype.scale,
                data_type_precision=sqltype.precision,
            )
            columns.append(column)
        return columns

    def _get_schemas(self) -> None:
        """
        Retrieves schemas in snowflake and saves them in the
        corrspeonding database
        """
        for database in self.databases.databases:
            filtered_schemas = [
                s.name
                for s in self.snf_root.databases[database.name].schemas.iter()
                if s.name.upper() not in ("PUBLIC", "INFORMATION_SCHEMA")
            ]
            for schema_name in filtered_schemas:
                schema = base.Schema(name=schema_name)
                self.databases_cache[database.name].schemas.append(schema)
                if database.name not in self.schemas:
                    self.schemas[database.name] = []
                self.schemas[database.name].append(schema)

    def _get_tables(self) -> None:
        """
        Retrieves tables in snowflake and saves them in the corresponding schema
        """
        for database in self.databases.databases:
            for schema in database.schemas:
                tables = (
                    self.snf_root.databases[database.name]
                    .schemas[schema.name]
                    .tables.iter(deep=not self.ignore_columns)
                )
                for table in tables:
                    if self.include_only_base_tables and table.table_type != "NORMAL":
                        continue

                    table_columns = []
                    if not self.ignore_columns:
                        table_columns = self._transform_table_columns(table.columns)

                    new_table = base.Table(
                        id=uuid.uuid4(),
                        name=table.name,
                        columns=table_columns,
                    )
                    schema.tables.append(new_table)

    def _transform(self) -> None:
        """Transform databases in a CLOE json format."""
        for database in self.databases.databases:
            if self.database_name_replace is not None:
                database.name = re.sub(
                    self.database_name_replace,
                    r"{{ CLOE_BUILD_CRAWLER_DB_REPLACEMENT }}",
                    database.name,
                )

    def to_json(self) -> str:
        return self.databases.model_dump_json(
            indent=4,
            by_alias=True,
            exclude_none=True,
        )

    def crawl(self) -> None:
        """
        Crawls a snowflake instance and saves metadata
        in a CLOE compatible format
        """
        self._get_databases()
        self._get_schemas()
        if not self.ignore_tables:
            self._get_tables()
        self._transform()
