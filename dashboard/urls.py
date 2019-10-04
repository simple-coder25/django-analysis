from django.contrib.auth.decorators import login_required
from django.urls import path

from dashboard import views


urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('upload/', login_required(views.UploadFieldView.as_view()), name='upload-files'),
    path('manage_files/', login_required(views.ManageFilesView.as_view()), name='manage-files'),
    path('delete_file/<int:pk>/', login_required(views.DeleteFileView.as_view()), name='delete-file'),
]
