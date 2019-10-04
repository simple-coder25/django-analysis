from django.db import models

from dashboard.models import UploadFileModel, FileColumnModel


INEQUALITY_CHOICES = (
    ('>', '>'),
    ('>=', '>='),
    ('==', '=='),
    ('<', '<'),
    ('<=', '<='),
)


class ValidationModel(models.Model):
    file = models.ForeignKey(UploadFileModel, on_delete=models.CASCADE)
    column = models.ForeignKey(FileColumnModel, on_delete=models.CASCADE)
    inequality = models.CharField(choices=INEQUALITY_CHOICES, max_length=30)
    value = models.FloatField()
    skip_row = models.BooleanField(default=False, blank=False)
    new_value = models.FloatField(blank=True, null=True)
    applied = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.column} {self.inequality} {self.value}'
