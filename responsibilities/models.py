from django.db import models
from django.utils.translation import gettext as _

from mainsite.models import Organization


class Tag(models.Model):
    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.name

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE
    )
    name = models.CharField(_("name"), max_length=200)


class Responsibility(models.Model):
    class Meta:
        verbose_name = _("Responsibility")
        verbose_name_plural = _("Responsibilities")
        ordering = ["name"]
    
    def __str__(self):
        return self.name

    organization = models.ForeignKey(
        Organization, related_name="responsibilities", on_delete=models.CASCADE
    )
    name = models.CharField(_("name"), max_length=500)
    description = models.CharField(
        _("description"), max_length=500, blank=True
    )
    link = models.URLField(_("link"), blank=True)
    tags = models.ManyToManyField(Tag)
    primary_employee = models.ForeignKey(
        "people.Employee", related_name="primary_responsibilities",
        null=True, on_delete=models.SET_NULL
    )
    secondary_employee = models.ForeignKey(
        "people.Employee", related_name="secondary_responsibilities",
        null=True, on_delete=models.SET_NULL
    )


