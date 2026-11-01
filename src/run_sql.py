import sys
from pathlib import Path

from src.db import get_connection
from src.logger import get_logger

logger = get_logger(__name__)

def run_sql_file(path):
    sql = Path(path).read_text()
    conn = get_connection()
    try:
        conn.cursor().execute(sql)
        conn.commit()
        logger.info('Ran %s', path)
    finally:
        conn.close()

if __name__ == '__main__':
    for path in sys.argv[1:]:
        run_sql_file(path)