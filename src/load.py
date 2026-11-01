import argparse

from src.config import RAW_DIR, REQUIRED_COLUMNS
from src.db import get_connection
from src.logger import get_logger
from src.validate import read_month, validate_month

logger = get_logger(__name__)

TEXT_COLUMNS = [
    'FlightDate', 'Reporting_Airline', 'Tail_Number', 'Origin', 'OriginCityName',
    'OriginState', 'Dest', 'DestCityName', 'DestState', 'CancellationCode',
]

CHUNK_SIZE = 50000

def prepare(df):
    df = df[REQUIRED_COLUMNS].copy()

    for col in REQUIRED_COLUMNS:
        if col not in TEXT_COLUMNS:
            df[col] = df[col].astype('Int64')
    return df

def load_to_staging(df, load_month):
    columns = ['load_month'] + REQUIRED_COLUMNS
    placeholders = ','.join('?' for _ in columns)
    insert_sql = (
        f'INSERT INTO staging.flights ({', '.join(columns)}) '
        f'VALUES ({placeholders})'
    )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.fast_executemany = True

    try:
        cursor.execute('TRUNCATE TABLE staging.flights')

        for start in range(0, len(df), CHUNK_SIZE):
            chunk = df.iloc[start:start + CHUNK_SIZE]
            chunk = chunk.astype(object).where(chunk.notna(), None)
            rows = [(load_month,) + tuple(r)
                    for r in chunk.itertuples(index=False, name=None)]
            cursor.executemany(insert_sql, rows)
            logger.info("Loaded %s of %s rows",
                        min(start + CHUNK_SIZE, len(df)), len(df))

        count = cursor.execute(
            'SELECT COUNT(*) FROM staging.flights WHERE load_month = ?',
            load_month).fetchone()[0]
        if count != len(df):
            raise RuntimeError(f'Row count mismatch: file {len(df)}, table {count}')

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--month', required=True, help='format: YYYY-MM')
    args = parser.parse_args()

    year, month = [int(x) for x in args.month.split('-')]
    load_month = f'{year}-{month:02d}'
    csv_path = RAW_DIR / f'ontime_{year}_{month:02d}.csv'

    df = read_month(csv_path)
    errors, warnings = validate_month(df, year, month)

    for w in warnings:
        logger.warning(w)

    if errors:
        for e in errors:
            logger.error(e)
        raise SystemExit(1)

    load_to_staging(prepare(df), load_month)
    logger.info('Staging load finished for %s', load_month)
        
