from django.db import models
from django.utils.functional import cached_property

from wagtail.snippets.models import register_snippet


@register_snippet
class OpeningTimes(models.Model):
    area = models.CharField(max_length=255)
    monday_open = models.TimeField(blank=True, null=True)
    monday_close = models.TimeField(blank=True, null=True)
    tuesday_open = models.TimeField(blank=True, null=True)
    tuesday_close = models.TimeField(blank=True, null=True)
    wednesday_open = models.TimeField(blank=True, null=True)
    wednesday_close = models.TimeField(blank=True, null=True)
    thursday_open = models.TimeField(blank=True, null=True)
    thursday_close = models.TimeField(blank=True, null=True)
    friday_open = models.TimeField(blank=True, null=True)
    friday_close = models.TimeField(blank=True, null=True)
    saturday_open = models.TimeField(blank=True, null=True)
    saturday_close = models.TimeField(blank=True, null=True)
    sunday_open = models.TimeField(blank=True, null=True)
    sunday_close = models.TimeField(blank=True, null=True)

    @cached_property
    def monday_hours(self):
        if self.monday_open and self.monday_close:
            return f"{self.monday_open.strftime('%H:%M')} - {self.monday_close.strftime('%H:%M')}"
        return "Closed"

    @cached_property
    def tuesday_hours(self):
        if self.tuesday_open and self.tuesday_close:
            return f"{self.tuesday_open.strftime('%H:%M')} - {self.tuesday_close.strftime('%H:%M')}"
        return "Closed"

    @cached_property
    def wednesday_hours(self):
        if self.wednesday_open and self.wednesday_close:
            return f"{self.wednesday_open.strftime('%H:%M')} - {self.wednesday_close.strftime('%H:%M')}"
        return "Closed"

    @cached_property
    def thursday_hours(self):
        if self.thursday_open and self.thursday_close:
            return f"{self.thursday_open.strftime('%H:%M')} - {self.thursday_close.strftime('%H:%M')}"
        return "Closed"

    @cached_property
    def friday_hours(self):
        if self.friday_open and self.friday_close:
            return f"{self.friday_open.strftime('%H:%M')} - {self.friday_close.strftime('%H:%M')}"
        return "Closed"

    @cached_property
    def saturday_hours(self):
        if self.saturday_open and self.saturday_close:
            return f"{self.saturday_open.strftime('%H:%M')} - {self.saturday_close.strftime('%H:%M')}"
        return "Closed"

    @cached_property
    def sunday_hours(self):
        if self.sunday_open and self.sunday_close:
            return f"{self.sunday_open.strftime('%H:%M')} - {self.sunday_close.strftime('%H:%M')}"
        return "Closed"

    @cached_property
    def weekly_hours(self):
        return [
            {
                "day": "Monday",
                "hours": self.monday_hours,
            },
            {
                "day": "Tuesday",
                "hours": self.tuesday_hours,
            },
            {
                "day": "Wednesday",
                "hours": self.wednesday_hours,
            },
            {
                "day": "Thursday",
                "hours": self.thursday_hours,
            },
            {
                "day": "Friday",
                "hours": self.friday_hours,
            },
            {
                "day": "Saturday",
                "hours": self.saturday_hours,
            },
            {
                "day": "Sunday",
                "hours": self.sunday_hours,
            },
        ]

    @cached_property
    def short_weekly_opening(self):
        open_days = []
        current_range = []
        for day in self.weekly_hours:
            if day["hours"] != "Closed":
                current_range.append(day["day"])
            else:
                if current_range:
                    if len(current_range) > 1:
                        open_days.append(f"{current_range[0]} - {current_range[-1]}")
                    else:
                        open_days.append(current_range[0])
                    current_range = []

        if current_range:
            if len(current_range) > 1:
                open_days.append(f"{current_range[0]} - {current_range[-1]}")
            else:
                open_days.append(current_range[0])

        return " and ".join(open_days)

    def __str__(self):
        return f"{self.area}"

    class Meta:
        verbose_name = "Opening time"
        verbose_name_plural = "Opening times"
