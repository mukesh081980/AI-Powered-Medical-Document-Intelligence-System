
import os
from pathlib import Path

import bcrypt
import mysql.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _setting(name, default=None):
    """Read Streamlit Secrets first, then local .env."""
    try:
        value = st.secrets.get(name, None)
    except Exception:
        value = None

    if value is None or value == "":
        value = os.getenv(name, default)

    return value


def connect_db():
    try:
        host = _setting("DB_HOST", "localhost")
        port = int(_setting("DB_PORT", "3306"))
        user = _setting("DB_USER")
        password = _setting("DB_PASSWORD")
        database = _setting("DB_NAME", "medisimplify")
        ssl_ca_value = _setting("DB_SSL_CA", "tidb-ca.pem")

        if not user or not password:
            raise ValueError(
                "DB_USER and DB_PASSWORD must be configured."
            )

        if not ssl_ca_value:
            raise ValueError("DB_SSL_CA must be configured.")

        ssl_ca_path = Path(ssl_ca_value)

        if not ssl_ca_path.is_absolute():
            ssl_ca_path = Path(__file__).resolve().parent / ssl_ca_path

        if not ssl_ca_path.is_file():
            raise FileNotFoundError(
                f"TiDB CA certificate not found: {ssl_ca_path}"
            )

        return mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connection_timeout=20,
            ssl_ca=str(ssl_ca_path),
            ssl_verify_cert=True,
            ssl_verify_identity=True
        )

    except (mysql.connector.Error, ValueError, OSError) as error:
        print(f"MySQL connection error: {error}")
        return None
