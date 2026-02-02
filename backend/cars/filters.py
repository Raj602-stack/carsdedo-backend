import django_filters
from django.db.models import Q, Count, Exists, OuterRef
from django.utils import timezone
from datetime import timedelta

from .models import (
    Car,
    InspectionItem,
)


class CarFilter(django_filters.FilterSet):
    """
    Marketplace-grade smart filtering for Cars
    Supports basic, advanced, inspection, dealer, media, JSON & search filters
    """

    # ------------------------------------------------------------------
    # PRICE
    # ------------------------------------------------------------------
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    exact_price = django_filters.NumberFilter(field_name="price")

    has_discount = django_filters.BooleanFilter(method="filter_has_discount")
    discount_price_min = django_filters.NumberFilter(field_name="discount_price", lookup_expr="gte")
    discount_price_max = django_filters.NumberFilter(field_name="discount_price", lookup_expr="lte")
    discount_percent_min = django_filters.NumberFilter(method="filter_discount_percent")

    # ------------------------------------------------------------------
    # IDENTIFIERS
    # ------------------------------------------------------------------
    car_code = django_filters.CharFilter(method="filter_in")

    # ------------------------------------------------------------------
    # BRAND / MODEL
    # ------------------------------------------------------------------
    brand = django_filters.CharFilter(method="filter_in")
    model = django_filters.CharFilter(method="filter_in")

    # ------------------------------------------------------------------
    # YEAR / KM
    # ------------------------------------------------------------------
    year_min = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="year", lookup_expr="lte")

    km_min = django_filters.NumberFilter(field_name="km", lookup_expr="gte")
    km_max = django_filters.NumberFilter(field_name="km", lookup_expr="lte")

    # ------------------------------------------------------------------
    # VEHICLE ATTRIBUTES
    # ------------------------------------------------------------------
    fuel = django_filters.CharFilter(method="filter_in")
    transmission = django_filters.CharFilter(method="filter_in")
    body = django_filters.CharFilter(method="filter_in")

    seats_min = django_filters.NumberFilter(field_name="seats", lookup_expr="gte")
    seats_exact = django_filters.NumberFilter(field_name="seats")

    color = django_filters.CharFilter(method="filter_color")

    # ------------------------------------------------------------------
    # LOCATION
    # ------------------------------------------------------------------
    city = django_filters.CharFilter(method="filter_in")
    rto = django_filters.CharFilter(method="filter_in")

    # ------------------------------------------------------------------
    # OWNERSHIP
    # ------------------------------------------------------------------
    owner_count = django_filters.NumberFilter()
    owner_count_lte = django_filters.NumberFilter(field_name="owner_count", lookup_expr="lte")
    first_owner_only = django_filters.BooleanFilter(method="filter_first_owner")

    # ------------------------------------------------------------------
    # INSURANCE
    # ------------------------------------------------------------------
    insurance_type = django_filters.CharFilter(method="filter_in")
    insurance_valid = django_filters.BooleanFilter(method="filter_insurance_valid")
    insurance_expired = django_filters.BooleanFilter(method="filter_insurance_expired")
    insurance_expiring_within_days = django_filters.NumberFilter(method="filter_insurance_expiring")

    # ------------------------------------------------------------------
    # AVAILABILITY
    # ------------------------------------------------------------------
    availability_status = django_filters.CharFilter(method="filter_in")

    # ------------------------------------------------------------------
    # DEALER
    # ------------------------------------------------------------------
    dealer_id = django_filters.UUIDFilter(field_name="dealer__id")
    dealer_tier = django_filters.CharFilter(method="filter_dealer_tier")
    dealer_city = django_filters.CharFilter(method="filter_dealer_city")
    dealer_code = django_filters.CharFilter(method="filter_dealer_code")

    # ------------------------------------------------------------------
    # MEDIA
    # ------------------------------------------------------------------
    has_thumbnail = django_filters.BooleanFilter(method="filter_thumbnail")
    image_count_min = django_filters.NumberFilter(method="filter_image_count")
    has_image_category = django_filters.CharFilter(method="filter_image_category")

    # ------------------------------------------------------------------
    # HIGHLIGHTS / REASONS
    # ------------------------------------------------------------------
    highlight_contains = django_filters.CharFilter(method="filter_highlight_contains")
    highlight_exact = django_filters.CharFilter(method="filter_highlight_exact")

    has_reason = django_filters.CharFilter(method="filter_reason_contains")
    reason_count_min = django_filters.NumberFilter(method="filter_reason_count")

    # ------------------------------------------------------------------
    # SPECS & FEATURES
    # ------------------------------------------------------------------
    spec = django_filters.CharFilter(method="filter_spec")

    has_features = django_filters.CharFilter(method="filter_features")
    feature_status = django_filters.CharFilter(method="filter_feature_status")
    feature_category = django_filters.CharFilter(method="filter_feature_category")

    # ------------------------------------------------------------------
    # INSPECTION
    # ------------------------------------------------------------------
    inspection_score_min = django_filters.NumberFilter(method="filter_inspection_score")
    inspection_rating = django_filters.CharFilter(method="filter_inspection_rating")
    inspection_subsection_status = django_filters.CharFilter(
        method="filter_inspection_subsection_status"
    )
    has_major_flaws = django_filters.BooleanFilter(method="filter_major_flaws")

    # ------------------------------------------------------------------
    # TAGS & METADATA
    # ------------------------------------------------------------------
    tags_any = django_filters.CharFilter(method="filter_tags_any")
    tags_all = django_filters.CharFilter(method="filter_tags_all")
    metadata = django_filters.CharFilter(method="filter_metadata")

    # ------------------------------------------------------------------
    # LISTING DATE
    # ------------------------------------------------------------------
    listed_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    listed_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")
    listed_last_n_days = django_filters.NumberFilter(method="filter_listed_last_n_days")

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Car
        fields = []

    # ==================================================================
    # FILTER METHODS
    # ==================================================================

    def filter_in(self, qs, name, value):
        return qs.filter(**{f"{name}__in": value.split(",")})

    def filter_color(self, qs, name, value):
        return qs.filter(colorKey__in=value.split(","))

    def filter_has_discount(self, qs, name, value):
        return qs.filter(discount_price__isnull=False) if value else qs

    def filter_discount_percent(self, qs, name, value):
        return qs.filter(
            discount_price__isnull=False,
            price__gt=0
        ).extra(
            where=["((price - discount_price) / price) * 100 >= %s"],
            params=[value],
        )

    def filter_first_owner(self, qs, name, value):
        return qs.filter(owner_count=1) if value else qs

    def filter_insurance_valid(self, qs, name, value):
        today = timezone.now().date()
        return qs.filter(insurance_valid_till__gte=today) if value else qs

    def filter_insurance_expired(self, qs, name, value):
        today = timezone.now().date()
        return qs.filter(insurance_valid_till__lt=today) if value else qs

    def filter_insurance_expiring(self, qs, name, value):
        today = timezone.now().date()
        return qs.filter(
            insurance_valid_till__range=(today, today + timedelta(days=value))
        )

    def filter_dealer_tier(self, qs, name, value):
        return qs.filter(dealer__tier__in=value.split(","))

    def filter_dealer_city(self, qs, name, value):
        return qs.filter(dealer__city__in=value.split(","))

    def filter_dealer_code(self, qs, name, value):
        return qs.filter(dealer__dealer_code__in=value.split(","))

    def filter_thumbnail(self, qs, name, value):
        return qs.filter(thumbnail__isnull=not value)

    def filter_image_count(self, qs, name, value):
        return qs.annotate(img_count=Count("images")).filter(img_count__gte=value)

    def filter_image_category(self, qs, name, value):
        return qs.filter(images__category__key__in=value.split(",")).distinct()

    def filter_highlight_contains(self, qs, name, value):
        return qs.filter(highlights__text__icontains=value)

    def filter_highlight_exact(self, qs, name, value):
        return qs.filter(highlights__text__iexact=value)

    def filter_reason_contains(self, qs, name, value):
        return qs.filter(reasons_to_buy__title__icontains=value)

    def filter_reason_count(self, qs, name, value):
        return qs.annotate(rc=Count("reasons_to_buy")).filter(rc__gte=value)

    def filter_spec(self, qs, name, value):
        # format: category_key:value
        key, val = value.split(":")
        return qs.filter(
            specs__category__key=key,
            specs__value__iexact=val
        )

    def filter_features(self, qs, name, value):
        for f in value.split(","):
            qs = qs.filter(features__name__iexact=f)
        return qs.distinct()

    def filter_feature_status(self, qs, name, value):
        return qs.filter(features__status=value)

    def filter_feature_category(self, qs, name, value):
        return qs.filter(features__category__key__in=value.split(","))

    def filter_inspection_score(self, qs, name, value):
        return qs.filter(inspection_section_scores__score__gte=value).distinct()

    def filter_inspection_rating(self, qs, name, value):
        return qs.filter(
            inspection_section_scores__rating__in=value.split(",")
        )

    def filter_inspection_subsection_status(self, qs, name, value):
        return qs.filter(
            inspection_subsection_remarks__status__in=value.split(",")
        )

    def filter_major_flaws(self, qs, name, value):
        subq = Exists(
            InspectionItem.objects.filter(
                car=OuterRef("pk"),
                status="major"
            )
        )
        return qs.annotate(has_major=subq).filter(has_major=value)

    def filter_tags_any(self, qs, name, value):
        q = Q()
        for tag in value.split(","):
            q |= Q(tags__contains=[tag])
        return qs.filter(q)

    def filter_tags_all(self, qs, name, value):
        for tag in value.split(","):
            qs = qs.filter(tags__contains=[tag])
        return qs

    def filter_metadata(self, qs, name, value):
        # format: key:value
        key, val = value.split(":")
        return qs.filter(**{f"metadata__{key}": val})

    def filter_listed_last_n_days(self, qs, name, value):
        return qs.filter(
            created_at__gte=timezone.now() - timedelta(days=value)
        )

    def filter_search(self, qs, name, value):
        return qs.filter(
            Q(title__icontains=value) |
            Q(brand__icontains=value) |
            Q(model__icontains=value) |
            Q(city__icontains=value) |
            Q(colorKey__icontains=value) |
            Q(car_code__icontains=value) |
            Q(registration_number__icontains=value)
        )
