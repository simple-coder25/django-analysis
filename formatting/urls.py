from django.contrib.auth.decorators import login_required
from django.urls import path

from formatting import views


urlpatterns = [
    path('', login_required(views.FormattingView.as_view()), name='add-formatters'),
    path('manage_formatters/', login_required(views.ManageFormattersView.as_view()), name='manage-formatters'),
    path('delete_formatter/<int:pk>/', login_required(views.DeleteFormatterView.as_view()), name='delete-formatter'),
    path('edit_formatter/<int:pk>/', login_required(views.EditFormatterView.as_view()), name='edit-formatter'),
    path('format_file/', login_required(views.FormatFileView.as_view()), name='format-file'),
]
