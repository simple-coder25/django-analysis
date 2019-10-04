import os

import pandas as pd
from django.shortcuts import render
from django.views import View

from core.settings import BASE_DIR
from dashboard.models import UploadFileModel, FileColumnModel
from formatting.forms import ValidationForm
from graphs.utils.frequency import frequency_dist


class GraphsView(View):
    model = UploadFileModel
    form_class = ValidationForm
    columns_model = FileColumnModel
    template_name = 'graphs/graphs.html'
    valid_extensions = ['.csv', '.tsv']
    valid_separators = {'.csv': ',', '.tsv': '\t'}
    sample_range = 0.05  # 5%

    def get(self, request, *args, **kwargs):
        context = {}

        files = self.model.objects.filter(author=self.request.user)
        file_id = self.request.GET.get('file_id')
        if file_id:
            file = self.model.objects.get(pk=file_id)
            form = ValidationForm(file=file)
            context['chose_file_form'] = form
        
        column_id = self.request.GET.get('column')
        if column_id:
            column_obj = self.columns_model.objects.get(pk=column_id)
            column_name = column_obj.column
            file_path = column_obj.file.file.url
            column_info = self.get_column_info(file_path, column_name)

            frequency_info = frequency_dist(column_info)

            context['line_dataset'] = column_info
            context['line_labels'] = list(range(len(column_info)))
            context['frequency_info'] = frequency_info
        context['files'] = files
        return render(request, self.template_name, context)

    def get_column_info(self, file_path, column):
        file_path = os.path.join('/', *BASE_DIR.split('/'), *file_path.split('/'))
        file_extension = os.path.splitext(file_path)[-1]
        if file_extension in self.valid_extensions:
            separator = self.valid_separators[file_extension]
            file_df = pd.read_csv(file_path, sep=separator)
            sample = file_df[column].sample(frac=self.sample_range, replace=True)
            values = sample.values.tolist()
            return values
