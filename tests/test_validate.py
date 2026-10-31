import pandas as pd

from src.config import REQUIRED_COLUMNS
from src.validate import validate_month


def make_sample(n=10, year=2024, month=1):
    df = pd.DataFrame({col: [0] * n for col in REQUIRED_COLUMNS})
    df['FlightDate'] = [f'{year}-{month:02d}-{(i % 28) + 1:02d}' for i in range(n)]
    df['Flight_Number_Reporting_Airline'] = list(range(n))
    return df


def test_good_file_passes():
    df = make_sample()
    errors, warnings = validate_month(df, 2024, 1, min_rows=5)
    assert errors == []


def test_missing_column_fails():
    df = make_sample().drop(columns=['ArrDelay'])
    errors, warnings = validate_month(df, 2024, 1, min_rows=5)
    assert len(errors) == 1
    assert 'Missing columns' in errors[0]


def test_wrong_month_fails():
    df = make_sample(month=2)
    errors, warnings = validate_month(df, 2024, 1, min_rows=5)
    assert any('outside' in e for e in errors)


def test_too_few_rows_fails():
    df = make_sample(n=3)
    errors, warnings = validate_month(df, 2024, 1, min_rows=5)
    assert any('rows, expected' in e for e in errors)


def test_missing_arrival_delay_fails():
    df = make_sample()
    df['ArrDelay'] = None
    errors, warnings = validate_month(df, 2024, 1, min_rows=5)
    assert any('ArrDelay' in e for e in errors)


def test_duplicate_flight_is_warning_not_error():
    df = make_sample()
    df['Flight_Number_Reporting_Airline'] = 1
    df['FlightDate'] = '2024-01-05'
    errors, warnings = validate_month(df, 2024, 1, min_rows=5)
    assert errors == []
    assert len(warnings) == 1


def test_cancelled_without_code_is_warning():
    df = make_sample()
    df.loc[0, 'Cancelled'] = 1
    df['CancellationCode'] = None
    errors, warnings = validate_month(df, 2024, 1, min_rows=5)
    assert any('cancellation code' in w for w in warnings)