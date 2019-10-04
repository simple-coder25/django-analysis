from django.db import models
from django.contrib.auth.models import User


class CustomUserModel(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    file_on_page = models.IntegerField(default=-1)

    def __str__(self):
        return f'{self.author}-{self.file_on_page}'


class UploadFileModel(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=50)
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f'{self.author}-{self.title}'

    def delete(self, *args, **kwargs):
        """
        Remove a file from media root and set file_on_page to default value when user delete a file
        """
        self.file.delete()
        CustomUserModel.objects.filter(author=self.author).update(file_on_page=-1)
        super(UploadFileModel, self).delete(*args, **kwargs)


class FileColumnModel(models.Model):
    COLUMN_TYPE_CHOICES = (
        ('numeric', 'numeric'),
        ('categorical', 'categorical'),
    )

    COLUMN_DEPENDENCE_CHOICES = (
        ('dependent', 'dependent'),
        ('independent', 'independent'),
    )

    file = models.ForeignKey(
        UploadFileModel,
        on_delete=models.CASCADE
    )
    column = models.CharField(max_length=100)
    type = models.CharField(choices=COLUMN_TYPE_CHOICES, default='numeric', max_length=20)
    dependence = models.CharField(choices=COLUMN_DEPENDENCE_CHOICES, default='dependent', max_length=20)

    def __str__(self):
        return f'{self.column} - {self.type}'

