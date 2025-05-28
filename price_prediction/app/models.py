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
    

class Property(models.Model):
    PROPERTY_TYPES = [
        ('House', 'House'),
        ('Apartment', 'Apartment'),
        ('Commercial', 'Commercial'),
        ('Land', 'Land'),
    ]
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    address = models.TextField()
    location = models.CharField(max_length=100)
    features = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    photos = models.ImageField(upload_to='property_photos/', blank=True, null=True)

    price = models.DecimalField(max_digits=12, decimal_places=2) 
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.property_type} at {self.location}"