from django.db import models
from django.contrib.auth.hashers import make_password, check_password

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class BuyerManager(models.Manager):
    def create_buyer(self, name, email, phone, address, gender, password, **extra_fields):
        buyer = self.model(
            name=name,
            email=email,
            phone=phone,
            address=address,
            gender=gender,
            **extra_fields
        )
        buyer.set_password(password)
        buyer.save(using=self._db)
        return buyer

class Buyer(models.Model):
    name = models.CharField(max_length=100)  
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = BuyerManager()

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.email
