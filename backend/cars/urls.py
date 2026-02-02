from rest_framework.routers import DefaultRouter
from .views import (
    CarListAPIView,
    CarDetailAPIView,
    CarCSVImportAPIView,
)
from django.urls import path


# router = DefaultRouter()
# router.register("cars", CarViewSet)
# router.register("dealers", DealerViewSet)

# urlpatterns = router.urls


urlpatterns = [
    path("cars/", CarListAPIView.as_view()),
    path("cars/<uuid:id>/", CarDetailAPIView.as_view()),
    path("cars/import/csv/", CarCSVImportAPIView.as_view()),
]

