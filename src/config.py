import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
LOG_DIR = BASE_DIR / 'logs'

BTS_URL = (
    "https://transtats.bts.gov/PREZIP/"
    "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip"
)

START_YEAR = 2024
START_MONTH = 1

AZURE_SQL_SERVER = os.getenv("AZURE_SQL_SERVER")
AZURE_SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE")
AZURE_SQL_USER = os.getenv("AZURE_SQL_USER")
AZURE_SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")

# Columns the pipeline needs from each monthly file
REQUIRED_COLUMNS = [
    'Year', 'Quarter', 'Month', 'DayofMonth', 'DayOfWeek', 'FlightDate',
    'Reporting_Airline', 'Tail_Number', 'Flight_Number_Reporting_Airline',
    'Origin', 'OriginCityName', 'OriginState',
    'Dest', 'DestCityName', 'DestState',
    'CRSDepTime', 'DepTime', 'DepDelay', 'DepDel15', 'TaxiOut', 'TaxiIn',
    'CRSArrTime', 'ArrTime', 'ArrDelay', 'ArrDel15',
    'Cancelled', 'CancellationCode', 'Diverted',
    'CRSElapsedTime', 'ActualElapsedTime', 'AirTime', 'Distance',
    'CarrierDelay', 'WeatherDelay', 'NASDelay', 'SecurityDelay', 'LateAircraftDelay',
]

# Columns that should identify one flight uniquely
KEY_COLUMNS = [
    'FlightDate', 'Reporting_Airline', 'Flight_Number_Reporting_Airline',
    'Origin', 'Dest', 'CRSDepTime',
]

# A normal month has roughly 500K+ flights
MIN_ROWS = 400000