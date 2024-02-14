import requests
from urllib.parse import quote_plus

from etna.records.models import Record


class RecordHasNoManifest(Exception):
    pass


def manifest_url_for_record(record: Record) -> str:
    """
    For the demo purposes.
    """
    iaid = quote_plus(record.iaid, safe="")
    url = f"https://ds-live-temp-iiif.s3.eu-west-2.amazonaws.com/manifests/{iaid}-manifest.json"
    
    # Check if we have the demo manifest on our S3 bucket with demo records,
    # and if we want to pretend that the given record has no manifest.
    response = requests.head(url, timeout=5)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise RecordHasNoManifest(iaid) from e
    return url
