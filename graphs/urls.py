from django.contrib.auth.decorators import login_required
from django.urls import path

from graphs import views


urlpatterns = [
    path('', login_required(views.GraphsView.as_view()), name='graphs'),
]