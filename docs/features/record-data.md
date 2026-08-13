# Record data

To fetch data from the Client API during development, a valid Rosetta API URL
needs to be added to `.env` (`ROSETTA_API_URL`). This will allow your container
to fetch the external data required to render explorer result and details
pages.

This feature is currently only used by the `RecordField` and `RecordChooserBlock`, which allows editors to input a record IAID, which then contacts the Rosetta API to retrieve the details for the given record IAID.
