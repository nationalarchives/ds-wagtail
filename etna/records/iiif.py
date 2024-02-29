from etna.records.models import Record


class RecordHasNoManifest(Exception):
    pass


DEMO_RECORDS = [
    "D7318973",
    "C11050044",
    "D7377268",
    "D7402444",
]


def manifest_url_for_record(record: Record) -> str:
    """
    Get a manifest URL for a specific Etna record.

    This is currently a mock implementation that returns a demo URL
    if the manifests are expected to exist in the demo S3 bucket.

    This won't longer be needed once the following issue is done:
    https://national-archives.atlassian.net/browse/DOR-22
    """
    if record.iaid not in DEMO_RECORDS:
        raise RecordHasNoManifest(record.iaid)

    return f"https://ds-live-temp-iiif.s3.eu-west-2.amazonaws.com/manifests/{record.iaid}-manifest.json"
