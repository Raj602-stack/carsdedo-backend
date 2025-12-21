

# class DealerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Dealer
#         fields = "__all__"


# class CarSerializer(serializers.ModelSerializer):
#     dealer = DealerSerializer(read_only=True)
#     dealer_code = serializers.CharField(write_only=True)

#     class Meta:
#         model = Car
#         fields = [
#             "id", "title", "brand", "model", "year", "price", "km",
#             "fuel", "transmission", "body", "city", "colorKey",
#             "image", "tags", "features",
#             "registration_number",
#             "dealer", "dealer_code",
#             "metadata", "created_at"
#         ]
#         read_only_fields = ("id", "created_at", "dealer")

#     def create(self, validated_data):
#         dealer_code = validated_data.pop("dealer_code")
#         dealer = Dealer.objects.get(dealer_code=dealer_code)
#         validated_data["dealer"] = dealer
#         return super().create(validated_data)


from rest_framework import serializers
from .models import *


# -------------------------
# DEALER MINI
# -------------------------
class DealerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        fields = ["id", "dealer_code", "name", "city", "tier"]


# -------------------------
# SIMPLE SERIALIZERS
# -------------------------
class CarHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarHighlight
        fields = ["text"]


class CarReasonToBuySerializer(serializers.ModelSerializer):
    class Meta:
        model = CarReasonToBuy
        fields = ["title", "description", "sort_order"]


class CarImageSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.key")

    class Meta:
        model = CarImage
        fields = ["category", "image", "caption", "sort_order"]


class CarSpecSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.key")

    class Meta:
        model = CarSpec
        fields = ["category", "label", "value"]


class CarFeatureSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.key")

    class Meta:
        model = CarFeature
        fields = ["category", "name"]


class InspectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionItem
        fields = ["name", "status", "remarks"]


# -------------------------
# CAR DETAIL SERIALIZER
# -------------------------
class CarDetailSerializer(serializers.ModelSerializer):
    dealer = DealerMiniSerializer(read_only=True)

    images = serializers.SerializerMethodField()
    highlights = CarHighlightSerializer(many=True)
    reasons_to_buy = CarReasonToBuySerializer(many=True)
    specs = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    inspections = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = "__all__"

    def get_images(self, obj):
        data = {}
        for img in obj.images.all():
            data.setdefault(img.category.key, []).append(
                CarImageSerializer(img).data
            )
        return data

    def get_specs(self, obj):
        data = {}
        for s in obj.specs.all():
            data.setdefault(s.category.key, []).append(
                CarSpecSerializer(s).data
            )
        return data

    def get_features(self, obj):
        data = {}
        for f in obj.features.all():
            data.setdefault(f.category.key, []).append(
                CarFeatureSerializer(f).data
            )
        return data

    def get_inspections(self, obj):
        result = []
        for section in InspectionSection.objects.all():
            subs = []
            for sub in section.subsections.all():
                items = obj.inspection_items.filter(subsection=sub)
                if items.exists():
                    subs.append({
                        "key": sub.key,
                        "title": sub.title,
                        "items": InspectionItemSerializer(items, many=True).data
                    })
            if subs:
                result.append({
                    "key": section.key,
                    "title": section.title,
                    "subsections": subs
                })
        return result
