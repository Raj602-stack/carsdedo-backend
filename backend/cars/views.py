# from rest_framework import viewsets, permissions, parsers
# from .models import Car, Dealer
# from .serializers import CarSerializer, DealerSerializer


# class DealerViewSet(viewsets.ModelViewSet):
#     queryset = Dealer.objects.all()
#     serializer_class = DealerSerializer
#     permission_classes = [permissions.AllowAny]


# class CarViewSet(viewsets.ModelViewSet):
#     queryset = Car.objects.all().order_by("-created_at")
#     serializer_class = CarSerializer
#     permission_classes = [permissions.AllowAny]
#     parser_classes = [
#         parsers.MultiPartParser,
#         parsers.FormParser,
#         parsers.JSONParser
#     ]



import csv
from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import *
from .serializers import *


# -------------------------
# LIST VIEW (CAR CARDS)
# -------------------------
class CarListAPIView(generics.ListAPIView):
    queryset = Car.objects.select_related("dealer")
    serializer_class = CarDetailSerializer


# -------------------------
# DETAIL VIEW
# -------------------------
class CarDetailAPIView(generics.RetrieveAPIView):
    queryset = Car.objects.select_related("dealer").prefetch_related(
        "images__category",
        "highlights",
        "reasons_to_buy",
        "specs__category",
        "features__category",
        "inspection_items__subsection__section",
    )
    serializer_class = CarDetailSerializer
    lookup_field = "id"


# -------------------------
# CSV IMPORT (SINGLE FILE)
# -------------------------
class CarCSVImportAPIView(APIView):
    """
    Dealer uploads ONE CSV.
    Dealer is inferred from request.user or passed explicitly.
    """

    def post(self, request):
        file = request.FILES["file"]
        dealer = Dealer.objects.get(id=request.data.get("dealer_id"))

        reader = csv.DictReader(file.read().decode("utf-8").splitlines())

        with transaction.atomic():
            for row in reader:
                car, _ = Car.objects.update_or_create(
                    registration_number=row["registration_number"],
                    dealer=dealer,
                    defaults={
                        "title": row["title"],
                        "brand": row["brand"],
                        "model": row["model"],
                        "year": row["year"],
                        "price": row["price"],
                        "km": row["km"],
                        "fuel": row["fuel"],
                        "transmission": row["transmission"],
                        "city": row["city"],
                    }
                )

                # Highlights
                for text in row["highlights"].split("|"):
                    CarHighlight.objects.get_or_create(car=car, text=text.strip())

                # Reasons
                for r in row["reasons_to_buy"].split("||"):
                    title, desc = r.split("::")
                    CarReasonToBuy.objects.update_or_create(
                        car=car,
                        title=title.strip(),
                        defaults={"description": desc.strip()}
                    )

        return Response(
            {"status": "CSV imported successfully"},
            status=status.HTTP_201_CREATED
        )
