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


class IAIDConverter(StringConverter):
    """Converter used to extract an IAID from a URL."""

    regex = r"([ACDFN][0-9]{1,8}|[a-f0-9]{8}-?([a-f0-9]{4}-?){3}[a-f0-9]{12}(_[1-9])?)"
