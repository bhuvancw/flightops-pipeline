import argparse

import pandas as pd

from src.config import RAW_DIR, REQUIRED_COLUMNS, KEY_COLUMNS, MIN_ROWS
from src.logger import get_logger

logger = get_logger(__name__)


def read_month(csv_path):
    header = pd.read_csv(csv_path, nrows=0).columns
    cols = [c for c in REQUIRED_COLUMNS if c in header]
    return pd.read_csv(csv_path, usecols=cols)


def validate_month(df, year, month, min_rows=MIN_ROWS):
    errors = []
    warnings = []

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f'Missing columns: {missing}')
        return errors, warnings

    if len(df) < min_rows:
        errors.append(f'Only {len(df)} rows, expected at least {min_rows}')

    dates = pd.to_datetime(df['FlightDate'], errors='coerce')
    wrong_dates = ((dates.dt.year != year) | (dates.dt.month != month)).sum()
    if wrong_dates > 0:
        errors.append(f'{wrong_dates} rows are outside {year}-{month:02d}')

    bad_flags = (~df['Cancelled'].isin([0, 1])).sum()
    if bad_flags > 0:
        errors.append(f'{bad_flags} rows have an invalid Cancelled value')

    # flights that actually flew should almost always have an arrival delay
    flown = df[(df['Cancelled'] == 0) & (df['Diverted'] == 0)]
    missing_share = flown['ArrDelay'].isnull().mean()
    if missing_share > 0.01:
        errors.append(f'ArrDelay is missing for {missing_share:.1%} of flown flights')

    cancelled = df[df['Cancelled'] == 1]
    no_code = cancelled['CancellationCode'].isnull().sum()
    if no_code > 0:
        warnings.append(f'{no_code} cancelled flights have no cancellation code')

    dupes = df.duplicated(subset=KEY_COLUMNS).sum()
    if dupes > 0:
        warnings.append(f'{dupes} rows repeat the flight key')

    return errors, warnings


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--month', required=True, help='format: YYYY-MM')
    args = parser.parse_args()

    year, month = [int(x) for x in args.month.split('-')]
    csv_path = RAW_DIR / f'ontime_{year}_{month:02d}.csv'

    df = read_month(csv_path)
    errors, warnings = validate_month(df, year, month)

    for w in warnings:
        logger.warning(w)

    if errors:
        for e in errors:
            logger.error(e)
        raise SystemExit(1)

    logger.info('Validation passed: %s rows', len(df))