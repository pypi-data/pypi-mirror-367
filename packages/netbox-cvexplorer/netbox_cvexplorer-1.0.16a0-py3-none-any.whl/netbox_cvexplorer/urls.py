from django.urls import path
from .views import CVEListView

app_name = 'netbox_cvexplorer' 
urlpatterns = [
    path('cve/', CVEListView.as_view(), name='cve_list'),
]