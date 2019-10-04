from allauth.account.forms import LoginForm
from django import forms

from dashboard.models import UploadFileModel


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFileModel
        exclude = ['author']
