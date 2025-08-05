from django.db import models
from django.utils import timezone


class FlightSessionQuerySet(models.QuerySet):
    def active(self):
        return self.filter(ended_at__isnull=True)

    def current(self):
        return self.active().first()

    async def acurrent(self):
        return await self.active().afirst()


class FlightSession(models.Model):
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    objects = FlightSessionQuerySet.as_manager()
