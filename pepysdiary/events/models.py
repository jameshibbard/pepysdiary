from django.db import models

from pepysdiary.common.models import OldDateMixin, PepysModel


class DayEvent(PepysModel, OldDateMixin):
    class Source(models.IntegerChoices):
        GADBURY = 10, "John Gadbury’s London Diary"
        PARLIAMENT = 20, "In Parliament"
        JOSSELIN = 30, "In Earl’s Colne, Essex"
        TIMEANDDATE = 40, "Times"

    title = models.CharField(max_length=255, blank=False, null=False)
    event_date = models.DateField(blank=False, null=False, db_index=True)
    url = models.URLField(max_length=255, blank=True, null=False)
    source = models.IntegerField(blank=True, null=True, choices=Source.choices)
    order = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Optionally used to order events when grouped by Source",
    )

    old_date_field = "event_date"

    class Meta:
        ordering = ["event_date"]
        verbose_name = "Day Event"

    def __str__(self):
        return self.title
