import argparse
import shutil
import zipfile

import requests

from src.config import BTS_URL, RAW_DIR
from src.logger import get_logger

logger = get_logger(__name__)


def download_month(year, month):
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    zip_path = RAW_DIR / f'ontime_{year}_{month:02d}.zip'
    csv_path = RAW_DIR / f'ontime_{year}_{month:02d}.csv'

    if csv_path.exists():
        logger.info('Already downloaded: %s', csv_path.name)
        return csv_path

    url = BTS_URL.format(year=year, month=month)
    logger.info('Downloading %s', url)

    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)

    with zipfile.ZipFile(zip_path) as z:
        csv_name = [n for n in z.namelist() if n.endswith('.csv')][0]
        with z.open(csv_name) as source, open(csv_path, 'wb') as target:
            shutil.copyfileobj(source, target)

    zip_path.unlink()

    if not csv_path.exists():
        raise FileNotFoundError(f'Extraction failed: {csv_path}')

    logger.info('Saved %s', csv_path.name)
    return csv_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--month', required=True, help='format: YYYY-MM')
    args = parser.parse_args()

    year, month = args.month.split('-')
    download_month(int(year), int(month))