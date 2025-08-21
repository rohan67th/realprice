from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid
from app.models import Property


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


class PasswordResetBuyer(models.Model):
    user = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"
    


class BuyerInterest(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    visit_scheduled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.buyer.username} -> {self.property.property_type}"



class VisitSchedule(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    is_notified = models.BooleanField(default=False)
    is_seen_by_buyer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.buyer.name} visit to {self.property}"
    

from app.models import CustomUser
class Message(models.Model):
    visit = models.ForeignKey(VisitSchedule, on_delete=models.CASCADE,related_name='chat_messages')
    sender_buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, null=True, blank=True)
    sender_seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = self.sender_buyer if self.sender_buyer else self.sender_seller
        return f"From {sender} at {self.timestamp}"
    


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ('listing_issue', 'Incorrect Listing'),
        ('seller_behavior', 'Seller Behavior'),
        ('fraud', 'Fraud/Security Issue'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]


    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='complaints')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint by {self.buyer} on {self.property}"
    



class RentRequest(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rent_requests')
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='rental_requests')
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Notification and payment tracking
    notified = models.BooleanField(default=False)  # Set True when seller approves
    is_paid = models.BooleanField(default=False)   # Set True after payment

    is_seen_by_buyer = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"RentRequest #{self.id} by {self.buyer.name} for {self.property.property_type}"