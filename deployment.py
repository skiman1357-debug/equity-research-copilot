"""Prepare reproducible data for Streamlit hosting."""
import hmac
import os
import tempfile
import threading
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from report_reader import REPORT_FILES, REPORTS_DIR, read_report
from setup_database import setup_database

REPORT_BASE_URL = 'https://investors.cyberfolks.pl/wp-content/uploads/2026/05/'
MAX_REPORT_BYTES = 40 * 1024 * 1024
_data_lock = threading.Lock()


def access_allowed(provided, expected):
    return bool(expected) and hmac.compare_digest(
        provided.encode('utf-8'), expected.encode('utf-8')
    )


def download_report(url, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={'User-Agent': 'EquityResearchCopilot/1.0'})
    temp_path = None
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.part', delete=False) as output:
                temp_path = Path(output.name)
                total = 0
                while chunk := response.read(64 * 1024):
                    total += len(chunk)
                    if total > MAX_REPORT_BYTES:
                        raise ValueError('Raport przekracza limit pobierania.')
                    output.write(chunk)
        ET.parse(temp_path)
        os.replace(temp_path, destination)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def prepare_data():
    with _data_lock:
        setup_database()
        for filename in REPORT_FILES:
            path = REPORTS_DIR / filename
            if not path.is_file():
                download_report(REPORT_BASE_URL + filename, path)
            pages = read_report(filename)
            if not pages or not any(page['text'].strip() for page in pages):
                raise ValueError('Raport nie zawiera czytelnych stron.')
