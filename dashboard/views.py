import os

import pandas as pd
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DeleteView

from core.settings import BASE_DIR
from dashboard.forms import UploadFileForm
from dashboard.models import UploadFileModel, CustomUserModel, FileColumnModel


class IndexView(ListView):
    model = UploadFileModel
    template_name = 'dashboard/table.html'
    context_object_name = 'files'
    valid_extensions = ['.csv', '.tsv']
    valid_separators = {'.csv': ',', '.tsv': '\t'}
    rows_count = 50

    def get_queryset(self):
        return UploadFileModel.objects.filter(author=self.request.user)

    def get(self, request, *args, **kwargs):
        CustomUserModel.objects.get_or_create(author=self.request.user)
        select = self.request.GET.get('select')
        if select:
            qs = CustomUserModel.objects.filter(author=self.request.user)
            qs.update(file_on_page=int(select))

        return super(IndexView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        file_exist = CustomUserModel.objects.filter(author=self.request.user).exists()
        if file_exist:
            file_id = CustomUserModel.objects.filter(author=self.request.user).get().file_on_page
            if file_id != -1:
                file_path = self.model.objects.get(pk=file_id).file.url
                file_name = self.model.objects.get(pk=file_id).title
                file_data = self.read_file(file_path)
                if file_data:
                    context.update({
                        'headers': file_data[-1],
                        'values': file_data[0].values(),
                        'file_name': file_name
                    })
                else:
                    context['error'] = f'Sorry, there are some errors with processing "{file_name}"'
            else:
                context['alert'] = 'Please, choose file for see rows'
        return context

    def read_file(self, file_path):
        file_path = os.path.join('/', *BASE_DIR.split('/'), *file_path.split('/'))
        file_extension = os.path.splitext(file_path)[-1]
        if file_extension in self.valid_extensions:
            separator = self.valid_separators[file_extension]
            file_df = pd.read_csv(file_path, sep=separator)
            dict_df = file_df[:self.rows_count].transpose().to_dict()
            headers = file_df.columns.values.tolist()
            return dict_df, headers


class UploadFieldView(FormView):
    form_class = UploadFileForm
    template_name = 'dashboard/upload.html'
    success_url = ''
    valid_extensions = ['.csv', '.tsv']
    valid_separators = {'.csv': ',', '.tsv': '\t'}

    def get_queryset(self):
        return UploadFileModel.objects.filter(author=self.request.user)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            column_info = self.get_columns_info(instance.file.url)
            if column_info:
                headers = column_info[0]
                types = column_info[1]
                for column in headers:
                    if types[column] in ['int64', 'float64']:
                        _type = 'numeric'
                    else:
                        _type = 'categorical'
                    FileColumnModel.objects.create(column=column, file=instance, type=_type)
            context = {
                'message': f'File {instance.title} was uploaded successfully'
            }
            return render(request, self.template_name, context=context)
        else:
            return self.form_invalid(form)

    def get_columns_info(self, file_path):
        file_path = os.path.join('/', *BASE_DIR.split('/'), *file_path.split('/'))
        file_extension = os.path.splitext(file_path)[-1]
        if file_extension in self.valid_extensions:
            separator = self.valid_separators[file_extension]
            file_df = pd.read_csv(file_path, sep=separator)
            headers = file_df.columns.values.tolist()
            types = file_df.dtypes.apply(lambda x: x.name).to_dict()
            return headers, types


class ManageFilesView(ListView):
    model = UploadFileModel
    template_name = 'dashboard/manage_files.html'
    context_object_name = 'files'

    def get_queryset(self):
        return UploadFileModel.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = context['object_list']
        if not object_list:
            context['empty_object_list'] = True
        return context


class DeleteFileView(DeleteView):
    model = UploadFileModel
    success_url = reverse_lazy('manage-files')
