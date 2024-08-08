from django.urls.converters import StringConverter


class ReferenceNumberConverter:
    """Converter used to extract a reference number from human-readable details route.

    Extracts the reference number PROB 1/4 (Shakeaspeare's Will) from:

    https://beta.nationalarchives.gov.uk/catalogue/PROB/1/4/

    Or reference numbers with dashes:

    LAB 2/1782/SandER106/1934/Part25and27-28and30to32

    From:

    https://beta.nationalarchives.gov.uk/catalogue/LAB/2/1782/SandER106/1934/Part25and27-28and30to32/

    """

    regex = r"(\w|/|-|~)+"

    def to_python(self, value):
        """Convert captured router parameters to reference number."""
        return value

    def to_url(self, value):
        """Convert reference number to create router parameter."""
        return value.replace(" ", "/")


class IDConverter(StringConverter):
    """Converter used to extract an IAID from a URL."""

    ohos_pattern = (
        r"media-[a-zA-Z0-9\-\.]{1,}"
        r"|wmk-[a-zA-Z0-9\-\.]{1,}"
        r"|swop-[a-zA-Z0-9\-\.]{1,}"
        r"|pcw-[a-zA-Z0-9\-\.]{1,}"
        r"|shc-[a-zA-Z0-9\-\.]{1,}"
        r"|osc-[a-zA-Z0-9\-\.]{1,}"
        r"|mpa-[0-9]{1,}"
        r"|sid-[a-zA-Z0-9\-\.]{1,}"
    )
    etna_pattern = (
        "[ACDFN][0-9]{1,8}|[a-f0-9]{8}-?([a-f0-9]{4}-?){3}[a-f0-9]{12}(_[1-9])?"
    )
    regex = rf"({ohos_pattern}|{etna_pattern})"
