import requests
from urllib.parse import quote_plus

from etna.records.models import Record


class RecordHasNoManifest(Exception):
    pass


class RecordManifestUnexpectedlyUnavailable(Exception):
    pass


def manifest_url_for_record(record: Record) -> str:
    """
    Get a manifest URL for a specific Etna record.

    This is currently a mock implementation that returns a demo URL
    if the manifests exists in the S3 bucket.

    In the future this would likely sit directly on the Record model
    instead.

    The S3 bucket is populated by manually created manifests:
    https://national-archives.atlassian.net/browse/DOR-7
    """
    # Clean the IAID to make it safe for use in a URL.
    iaid = quote_plus(record.iaid, safe="")

    url = f"https://ds-live-temp-iiif.s3.eu-west-2.amazonaws.com/manifests/{iaid}-manifest.json"

    # Check if we have the demo manifest on our S3 bucket with demo records,
    # and if we do not we want to pretend that the given record has no manifest.
    response = requests.head(url, timeout=5)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise RecordHasNoManifest(iaid) from e
    except requests.exceptions.RequestException as e:
        raise RecordManifestUnexpectedlyUnavailable(iaid) from e
    return url
