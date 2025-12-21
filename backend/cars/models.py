import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


# -------------------------
# Custom User
# -------------------------
class UserManager(BaseUserManager):
    def create_user(self, phone_number=None, email=None, password=None, **extra):
        if not phone_number and not email:
            raise ValueError("Either phone number or email is required")

        if email:
            email = self.normalize_email(email)

        user = self.model(phone_number=phone_number, email=email, **extra)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number=None, email=None, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(phone_number, email, password, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email or self.phone_number or str(self.id)


# -------------------------
# OTP
# -------------------------
class OTP(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).total_seconds() > 300

    def __str__(self):
        return f"{self.phone_number} - {self.code}"


# -------------------------
# Dealer
# -------------------------
# class Dealer(models.Model):
#     TIER_CHOICES = [
#         ("standard", "Standard"),
#         ("premium", "Premium"),
#         ("vip", "VIP"),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     dealer_code = models.CharField(max_length=32, unique=True)
#     name = models.CharField(max_length=255)

#     phone = models.CharField(max_length=20, blank=True)
#     email = models.EmailField(blank=True)

#     address = models.TextField(blank=True)
#     city = models.CharField(max_length=120, blank=True)
#     state = models.CharField(max_length=120, blank=True)
#     postal_code = models.CharField(max_length=20, blank=True)

#     tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="standard")
#     tags = models.JSONField(default=list, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.dealer_code} - {self.name}"


# # -------------------------
# # Car
# # -------------------------
# class Car(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     title = models.CharField(max_length=255)
#     brand = models.CharField(max_length=100, blank=True)
#     model = models.CharField(max_length=100, blank=True)

#     year = models.PositiveIntegerField(null=True, blank=True)
#     price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     km = models.PositiveIntegerField(null=True, blank=True)

#     fuel = models.CharField(max_length=50, blank=True)
#     transmission = models.CharField(max_length=50, blank=True)
#     body = models.CharField(max_length=50, blank=True)

#     city = models.CharField(max_length=100, blank=True)
#     colorKey = models.CharField(max_length=50, blank=True)

#     image = models.ImageField(upload_to="cars/", null=True, blank=True)

#     tags = models.JSONField(default=list, blank=True)
#     features = models.JSONField(default=list, blank=True)

#     registration_number = models.CharField(max_length=50, blank=True)

#     dealer = models.ForeignKey(
#         Dealer,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=False,
#         related_name="cars",
#     )

#     metadata = models.JSONField(default=dict, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title



import uuid
from django.db import models


# -------------------------
# Dealer (UNCHANGED)
# -------------------------
class Dealer(models.Model):
    TIER_CHOICES = [
        ("standard", "Standard"),
        ("premium", "Premium"),
        ("vip", "VIP"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dealer_code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)

    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default="standard")
    tags = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dealer_code} - {self.name}"


# -------------------------
# Car (ROOT ENTITY)
# -------------------------
class Car(models.Model):
    print("🚀 cars.models loaded")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    car_code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True
    )

    dealer = models.ForeignKey(
        Dealer,
        on_delete=models.SET_NULL,
        null=True,
        related_name="cars",
    )

    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)

    year = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    km = models.PositiveIntegerField(null=True, blank=True)

    fuel = models.CharField(max_length=50, blank=True)
    transmission = models.CharField(max_length=50, blank=True)
    body = models.CharField(max_length=50, blank=True)

    city = models.CharField(max_length=100, blank=True)
    colorKey = models.CharField(max_length=50, blank=True)

    thumbnail = models.ImageField(upload_to="cars/thumbnails/", null=True, blank=True)

    registration_number = models.CharField(max_length=50, blank=True)

    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# -------------------------
# IMAGE SYSTEM
# -------------------------
class CarImageCategory(models.Model):
    key = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)

    def __str__(self):
        return self.label


class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="images")
    category = models.ForeignKey(CarImageCategory, on_delete=models.PROTECT)
    image = models.ImageField(upload_to="cars/images",max_length=255)  # path or URL
    caption = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)


# -------------------------
# HIGHLIGHTS
# -------------------------
class CarHighlight(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="highlights")
    text = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["car", "text"],
                name="unique_car_highlight"
            )
        ]

     



# -------------------------
# REASONS TO BUY
# -------------------------


class CarReasonToBuy(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reasons_to_buy")
    title = models.CharField(max_length=200)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["car", "title"],
                name="unique_car_reason_to_buy"
            )
        ]


# -------------------------
# SPECS
# -------------------------
class SpecCategory(models.Model):
    key = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)



class CarSpec(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="specs")
    category = models.ForeignKey(SpecCategory, on_delete=models.CASCADE)
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["car", "category", "label"],
                name="unique_car_spec"
            )
        ]



# -------------------------
# FEATURES
# -------------------------
class FeatureCategory(models.Model):
    key = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)




class CarFeature(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="features")
    category = models.ForeignKey(FeatureCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["car", "category", "name"],
                name="unique_car_feature"
            )
        ]


# -------------------------
# INSPECTION SYSTEM
# -------------------------
class InspectionSection(models.Model):
    key = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)


class InspectionSubSection(models.Model):
    section = models.ForeignKey(
        InspectionSection,
        on_delete=models.CASCADE,
        related_name="subsections",
    )
    key = models.CharField(max_length=50)
    title = models.CharField(max_length=100)


class InspectionItem(models.Model):
    STATUS_CHOICES = [
        ("flawless", "Flawless"),
        ("minor", "Minor"),
        ("major", "Major"),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="inspection_items")
    subsection = models.ForeignKey(InspectionSubSection, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["car", "subsection", "name"],
                name="unique_inspection_item_per_car"
            )
        ]