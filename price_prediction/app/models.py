from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, phone, address, gender,password=None,**extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            phone=phone,
            address=address,
            gender=gender,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email,password,**extra_fields):
        user = self.create_user(
            username=username,
            email=email,
            phone='N/A',
            address='N/A',
            gender='Other',
            password=password,
            **extra_fields
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    gender = models.CharField(max_length=10)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    proof_of_identity = models.FileField(upload_to='identity_proofs/', null=True, blank=True)
    
    is_blocked = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class PasswordReset(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"
    


from django.utils.text import slugify
from django.conf import settings

class Property(models.Model):
    PROPERTY_TYPES = [
        ('House', 'House'),
        ('Apartment', 'Apartment'),
        ('Commercial', 'Commercial'),
        ('Land', 'Land'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Sold', 'Sold'),
        ('Rented', 'Rented'),
    ]

    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    address = models.TextField()
    location = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    area_sqft = models.FloatField(null=True, blank=True)
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)

    features = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    main_image = models.ImageField(upload_to='property_photos/', null=True, blank=True)
    image_1 = models.ImageField(upload_to='property_photos/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='property_photos/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='property_photos/', null=True, blank=True)

    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')

    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    posted_at = models.DateTimeField(auto_now_add=True)

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.property_type}-{self.location}-{self.pk}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.property_type} at {self.location} - ₹{self.price}"
