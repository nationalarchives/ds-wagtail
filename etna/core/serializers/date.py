from rest_framework.serializers import Serializer


class DateTimeSerializer(Serializer):
    """
    Serializer used to split a date into individual fields for use in the API.
    e.g.
    {
        "value": "2000-01-01",
        "year": 2000,
        "month": 1,
        "day": 1
    }

    or if there is a time component:
    {
        "value": "2000-01-01T12:00:00",
        "year": 2000,
        "month": 1,
        "day": 1,
        "hour": 12,
        "minute": 0,
        "second": 0
    }
    """

    def to_representation(self, value):
        time_data = {}
        if value.hour or value.minute or value.second:
            time_data = {
                "hour": value.hour,
                "minute": value.minute,
                "second": value.second,
            }
        return {
            "value": value,
            "year": value.year,
            "month": value.month,
            "day": value.day,
            **(time_data),
        }
