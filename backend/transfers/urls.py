from django.urls import path
from transfers.views import TransferJobView, TransferJobDetailView

urlpatterns = [
    path("transfer/", TransferJobView.as_view(), name = "transfer-job-create"),
    path("transfer/<int:job_id>/", TransferJobDetailView.as_view(), name = "transfer-job-detail"),
]

