import os

import pandas as pd
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView, UpdateView

from core.settings import BASE_DIR
from dashboard.models import UploadFileModel, FileColumnModel, CustomUserModel
from formatting.forms import ValidationForm
from formatting.models import ValidationModel


class FormattingView(View):
    model = UploadFileModel
    form_class = ValidationForm
    columns_model = FileColumnModel
    template_name = 'formatting/add_formatters.html'

    def get(self, request, *args, **kwargs):
        context = {}
        
        files = self.model.objects.filter(author=self.request.user)
        file_id = self.request.GET.get('file_id')
        if file_id:
            file = self.model.objects.get(pk=file_id)
            form = ValidationForm(file=file)
            context['chose_file_form'] = form
        context['files'] = files
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {}
       
        file_id = self.request.GET.get('file_id')
        file = self.model.objects.get(pk=file_id)
        form = self.form_class(file, request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.file = file
            instance.save()
            context['message'] = 'Validator was added successfully'
        return render(request, self.template_name, context)


class ManageFormattersView(ListView):
    model = ValidationModel
    template_name = 'formatting/manage_formatters.html'
    context_object_name = 'formatters'

    def get_queryset(self):
        files = UploadFileModel.objects.filter(author=self.request.user)
        return self.model.objects.filter(file__in=files)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = context['object_list']
        if not object_list:
            context['empty_object_list'] = True
        return context

    def post(self, request, *args, **kwargs):
        qs = self.get_queryset()
        for obj in qs:
            obj.applied = True
            obj.save()
        return redirect(reverse_lazy('manage-formatters'))


class DeleteFormatterView(DeleteView):
    model = ValidationModel
    success_url = reverse_lazy('manage-formatters')


class EditFormatterView(UpdateView):
    model = ValidationModel
    form_class = ValidationForm
    template_name = 'formatting/edit_formatters.html'
    success_url = reverse_lazy('manage-formatters')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get(self.pk_url_kwarg)
        obj = self.model.objects.get(pk=pk)
        file = obj.file
        form = self.form_class(file=file, instance=obj)

        context.update({
            'form': form
        })

        return context


class FormatFileView(View):
    model = UploadFileModel
    form_class = ValidationForm
    columns_model = FileColumnModel
    template_name = 'dashboard/table.html'
    valid_extensions = ['.csv', '.tsv']
    valid_separators = {'.csv': ',', '.tsv': '\t'}
    rows_count = 1000

    @staticmethod
    def formatters_to_dict(formatters):
        result = []
        for obj in formatters:
            result.append({
                'column': obj.column.column,
                'inequality': obj.inequality,
                'value': obj.value,
                'skip_row': obj.skip_row,
                'new_value': obj.new_value,
            })
        return result

    def get(self, request, *args, **kwargs):
        context = {}

        file_id = CustomUserModel.objects.filter(author=self.request.user).get().file_on_page
        file_obj = self.model.objects.get(pk=file_id)
        file_path = file_obj.file.url
        formatters_qs = ValidationModel.objects.filter(file=file_obj).filter(applied=True)

        if not formatters_qs:
            context['error'] = "You don't have any formatters"
            return render(request, self.template_name, context)

        formatters = self.formatters_to_dict(formatters_qs)
        file_df = self.read_file(file_path)
        processed_df = self.process_df(file_df, formatters)

        self.update_file(file_path, processed_df)

        return redirect(reverse_lazy('index'))

    def read_file(self, file_path):
        file_path = os.path.join('/', *BASE_DIR.split('/'), *file_path.split('/'))
        file_extension = os.path.splitext(file_path)[-1]
        if file_extension in self.valid_extensions:
            separator = self.valid_separators[file_extension]
            file_df = pd.read_csv(file_path, sep=separator)
            return file_df

    def update_file(self, file_path, df):
        file_path = os.path.join('/', *BASE_DIR.split('/'), *file_path.split('/'))
        file_extension = os.path.splitext(file_path)[-1]
        separator = self.valid_separators[file_extension]
        
        df.to_csv(file_path, sep=separator, index=False)

    @staticmethod
    def process_df(df, formatters):

        def process_column(old_value, inequality, value, new_value):
            if inequality == '==':
                if old_value == value:
                    return new_value if new_value is not None else old_value
            elif inequality == '<':
                if old_value < value:
                    return new_value if new_value is not None else old_value
            elif inequality == '<=':
                if old_value <= value:
                    return new_value if new_value is not None else old_value
            elif inequality == '>':
                if old_value > value:
                    return new_value if new_value is not None else old_value
            elif inequality == '>=':
                if old_value >= value:
                    return new_value if new_value is not None else old_value
            return old_value

        def filter_df(df, column, inequality, value):

            if inequality == '==':
                df_filtered = df[df[column] != value]
            elif inequality == '<':
                df_filtered = df[df[column] >= value]
            elif inequality == '<=':
                df_filtered = df[df[column] > value]
            elif inequality == '>':
                df_filtered = df[df[column] <= value]
            elif inequality == '>=':
                df_filtered = df[df[column] < value]
            else:
                df_filtered = df
            return df_filtered

        for formatter in formatters:
            column = formatter['column']
            inequality = formatter['inequality']
            value = formatter['value']
            skip_row = formatter['skip_row']
            new_value = formatter['new_value']

            if skip_row:
                df = filter_df(df, column, inequality, value)

            df[column] = df[column].map(lambda v: process_column(v, inequality, value, new_value))

        return df
