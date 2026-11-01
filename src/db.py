import time

import pyodbc

from src.config import (AZURE_SQL_SERVER, AZURE_SQL_DATABASE,
                        AZURE_SQL_USER, AZURE_SQL_PASSWORD)
from src.logger import get_logger

logger = get_logger(__name__)


def pick_driver():
    drivers = [d for d in pyodbc.drivers()
               if d.startswith('ODBC Driver') and 'SQL Server' in d]
    if not drivers:
        raise RuntimeError('No ODBC Driver for SQL Server found')
    for d in drivers:
        if '18' in d:
            return d
    return drivers[0]


def get_connection(retries=3, wait=30):
    driver = pick_driver()
    conn_str = (
        f'DRIVER={{{driver}}};'
        f'SERVER={AZURE_SQL_SERVER};'
        f'DATABASE={AZURE_SQL_DATABASE};'
        f'UID={AZURE_SQL_USER};'
        f'PWD={AZURE_SQL_PASSWORD};'
        'Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;'
    )

    for attempt in range(1, retries + 1):
        try:
            return pyodbc.connect(conn_str)
        except pyodbc.Error as e:
            logger.warning('Connection attempt %s failed: %s', attempt, e)
            if attempt == retries:
                raise
            time.sleep(wait)


if __name__ == '__main__':
    logger.info('Using driver: %s', pick_driver())
    conn = get_connection()
    row = conn.cursor().execute('SELECT DB_NAME(), @@VERSION').fetchone()
    logger.info('Connected to %s', row[0])
    conn.close()