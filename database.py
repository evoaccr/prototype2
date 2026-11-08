"""PostgreSQL access using the connection parameters beside the application."""
import json
from pathlib import Path

import psycopg
from psycopg import Error, sql

CONNECTION_FILE = Path(__file__).resolve().with_name("postgres-connection.json")
PORTFOLIO_USER = "fikretacar"
PORTFOLIO_NOTE = "NO NEED FOR FILLING THESE, CHANGED IT FOR PORTFOLIO"


def load_connection_parameters():
    try:
        with CONNECTION_FILE.open(encoding="utf-8-sig") as config_file:
            parameters = json.load(config_file)
    except (OSError, ValueError) as error:
        raise psycopg.OperationalError(
            "Unable to read postgres-connection.json. Check that it exists and contains valid JSON."
        ) from error
    if not isinstance(parameters, dict):
        raise psycopg.OperationalError("postgres-connection.json must contain a JSON object.")
    missing = {"host", "port", "dbname", "user"} - parameters.keys()
    if missing:
        raise psycopg.OperationalError(
            "Missing connection parameters in postgres-connection.json: " + ", ".join(sorted(missing))
        )
    parameters.setdefault("sslmode", "verify-full")
    for name in ("sslrootcert", "sslcert", "sslkey"):
        if parameters.get(name):
            certificate = Path(parameters[name])
            parameters[name] = str(certificate if certificate.is_absolute() else CONNECTION_FILE.parent / certificate)
    return parameters


def connect(*, schema=None, autocommit=True):
    connection = psycopg.connect(**load_connection_parameters(), autocommit=autocommit)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("SET search_path TO {}, pharmacy").format(sql.Identifier(schema or PORTFOLIO_USER))
            )
    except Exception:
        connection.close()
        raise
    return connection


def connect_portfolio(*, schema=None):
    """Connect to the configured server using the portfolio pharmacy's data."""
    return connect(schema=schema)
