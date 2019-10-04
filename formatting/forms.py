from django import forms

from dashboard.models import FileColumnModel
from formatting.models import ValidationModel


class ValidationForm(forms.ModelForm):
    class Meta:
        model = ValidationModel
        exclude = ['file']

    def __init__(self, file=None, *args, **kwargs):
        super(ValidationForm, self).__init__(*args, **kwargs)
        if file:
            self.fields['column'].queryset = FileColumnModel.objects.filter(file=file).filter(type='numeric')
