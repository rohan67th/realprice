from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser,PasswordReset,Property
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseBadRequest, HttpResponseRedirect



#Admin

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials or not authorized as admin")

    return render(request, 'admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect("/")

from django.core.mail import send_mail

def approve_seller(request, seller_id):
    seller = get_object_or_404(CustomUser, id=seller_id)
    seller.is_approved = True
    seller.save()

    send_mail(
        subject='Your Seller Account Has Been Approved',
        message='Hi {},\n\nYour seller account has been approved! You can now log in and start using the platform.'.format(seller.username),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[seller.email],
        fail_silently=False,
    )

    messages.success(request, f"{seller.email} has been approved and notified.")
    return redirect('dashboard')

def decline_seller(request, seller_id):
    seller = get_object_or_404(CustomUser, id=seller_id)

    send_mail(
        subject='Your Seller Account Has Been Declined',
        message='Hi {},\n\nWe’re sorry, but your seller account request has been declined.'.format(seller.username),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[seller.email],
        fail_silently=False,
    )

    seller.delete()
    messages.warning(request, f"{seller.email} has been declined and notified.")
    return redirect('dashboard')


def seller_list(request):
    users = CustomUser.objects.filter(is_approved=True, is_superuser=False)
    return render(request, 'seller_list.html', {'users': users})

def buyer_list(request):
    buyers = Buyer.objects.all()
    return render(request, 'buyer_list.html', {'buyers': buyers})


def toggle_block_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    return redirect('seller_list')


def approve_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    property_obj.is_approved = True
    property_obj.save()
    messages.success(request, f'Property "{property_obj}" approved successfully.')
    return redirect('dashboard')


def decline_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    property_obj.delete()  
    messages.success(request, f'Property "{property_obj}" declined and removed.')
    return redirect('dashboard')


def admin_property_list(request):
    properties = Property.objects.filter(is_approved=True)
    return render(request,'admin_property_list.html',{'properties': properties})


from buyer.models import Complaint

def complaints_admin_view(request):
    complaints = Complaint.objects.select_related('property', 'buyer').order_by('-created_at')
    context = {
        'complaints': complaints
    }
    return render(request, 'admin_complaints_list.html', context)


def delete_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)

    if request.method == "POST":
        property_obj.delete()
        messages.success(request, "Property deleted successfully.")
        return redirect('admin_property_list') 

    messages.error(request, "Invalid request method.")
    return redirect('admin_property_list')


def delete_buyer(request, buyer_id):
    if request.method == 'POST':
        buyer = get_object_or_404(Buyer, id=buyer_id)
        buyer.delete()
        messages.success(request, "Buyer deleted successfully.")
    return redirect('buyer_list')



#Seller
import re

MAX_FILE_SIZE_MB = 2  # Max 2MB
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024


def is_strong_password(password):
    # At least 6 characters, one letter, one digit, one special character
    return (
        len(password) >= 6 and
        re.search(r"[A-Za-z]", password) and
        re.search(r"\d", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def seller_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_pic = request.FILES.get('profile_pic')
        proof_of_identity = request.FILES.get('proof_of_identity')

        if not re.search(r'[A-Za-z]', username):
            messages.error(request, "Username should contain only letters.")
            return redirect('register')
        
        if not re.fullmatch(r'^[0-9]{10}$', phone):
            messages.error(request, "Enter a valid 10-digit phone number.")
            return redirect('register')
        
        if proof_of_identity and proof_of_identity.size > MAX_FILE_SIZE:
            messages.error(request, f"File size exceeds limit of {MAX_FILE_SIZE_MB}MB.")
            return redirect('register')
        

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        
        if not is_strong_password(password):
            messages.error(request, "Password must be at least 6 characters with letters, numbers, and a special character.")
            return redirect('register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            phone=phone,
            address=address,
            gender=gender,
            profile_pic=profile_pic,
            password=password,
            proof_of_identity=proof_of_identity,
        )

        login(request, user)
        return redirect('login')

    return render(request, 'register.html')

def seller_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_blocked:
                messages.error(request, "Your account has been blocked by the admin.")
                return redirect('login')
            if user.is_approved:
                login(request, user)
                profile_url = reverse('seller_profile', kwargs={'user_id': user.id})
                return redirect(profile_url)
            else:
                messages.error(request, "Your account is pending admin approval.")
                return redirect('login')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def seller_profile(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    
    visit = VisitSchedule.objects.filter(
        property__seller=user,
        status='approved'
    ).first()

    return render(request, 'seller_profile.html', {
        'user': user,
        'visit': visit,
    })

def seller_property_list(request):
    properties = Property.objects.filter(is_approved=True)
    return render(request,'seller_property_list.html',{'properties': properties})


def seller_edit_property(request, id):
    property = get_object_or_404(Property, id=id)
    if request.method == 'POST':
        property.title = request.POST.get('title')
        property.location = request.POST.get('location')
        property.property_type = request.POST.get('property_type')
        property.price = request.POST.get('price')
        property.status = request.POST.get('status')
        property.save()
        messages.success(request, 'Property updated successfully.')
        return redirect('seller_property_list')
    return render(request, 'edit_property.html', {'property': property})


def seller_delete_property(request, id):
    property = get_object_or_404(Property, id=id)
    property.delete()
    messages.success(request, 'Property deleted successfully.')
    return redirect('seller_property_list')


def seller_pending_properties(request):
    properties = Property.objects.filter(is_approved=False)
    return render(request, 'seller_pending_properties.html', {'properties': properties})


#Property Management

def add_property(request):
    if request.method == 'POST':
        property_type = request.POST.get('property_type')
        address = request.POST.get('address')
        location = request.POST.get('location')
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None
        area_sqft = request.POST.get('area_sqft') or None
        bedrooms = request.POST.get('bedrooms') or None
        bathrooms = request.POST.get('bathrooms') or None
        features = request.POST.get('features', '')
        description = request.POST.get('description', '')
        status = request.POST.get('status', 'Available')
        price = request.POST.get('price')

        # Fetch all image fields from request.FILES
        main_image = request.FILES.get('main_image')
        image_1 = request.FILES.get('image_1')
        image_2 = request.FILES.get('image_2')
        image_3 = request.FILES.get('image_3')

        from decimal import Decimal, InvalidOperation
        try:
            price_decimal = Decimal(price)
        except (InvalidOperation, TypeError):
            price_decimal = None

        if price_decimal is not None:
            property = Property.objects.create(
                property_type=property_type,
                address=address,
                location=location,
                latitude=latitude,
                longitude=longitude,
                area_sqft=area_sqft,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                features=features,
                description=description,
                price=price_decimal,
                status=status,
                seller=request.user,
                main_image=main_image,
                image_1=image_1,
                image_2=image_2,
                image_3=image_3,
                is_approved=False
            )
            messages.success(request, 'Property added and pending admin approval.')
            return redirect('property_list', seller_id=request.user.id)
        else:
            messages.error(request, 'Invalid price entered.')

    return render(request, 'add_property.html')




def property_list(request, seller_id):
    seller = get_object_or_404(CustomUser, id=seller_id)  # Fetch seller from URL param
    properties = Property.objects.filter(seller=seller, is_approved=True)  # Filter by seller
    return render(request, 'property_list.html', {
        'seller': seller,
        'properties': properties,
    })


def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'property_detail.html', {'property': property})


#Forget password

def forget_password(request):
    
    if request.method =="POST":
        email = request.POST.get('email')

        try:
            user = CustomUser.objects.get(email=email)

            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
        

            email_message = EmailMessage(
                'Reset your password',
                email_body,
                settings.EMAIL_HOST_USER,
                [email]
            )

            email_message.fail_silently = False
            email_message.send()

            return HttpResponseRedirect(reverse("password-reset-sent", kwargs={"reset_id": new_password_reset.reset_id}))
        
        except CustomUser.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request,'forget_password.html')


def password_reset_sent(request,reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')


def reset_password(request,reset_id):
    
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')
            
            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            
            else:
                return redirect('reset-password',reset_id=reset_id)

    
    
    except PasswordReset.DoesNotExist:
        
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html',{'reset_id': reset_id})

def edit_profile(request):
    user = CustomUser.objects.get(email=request.user.email)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.gender = request.POST.get('gender')

        # Handle profile picture if uploaded
        if 'profile_pic' in request.FILES:
            user.profile_pic = request.FILES['profile_pic']

        # Handle proof of identity if uploaded
        if 'proof_of_identity' in request.FILES:
            user.proof_of_identity = request.FILES['proof_of_identity']

        user.save()

        messages.success(request, "Profile updated successfully!")
        profile_url = reverse('seller_profile', kwargs={'user_id': user.id})
        return redirect(profile_url)

    return render(request, 'edit_seller.html', {'user': user})



def landingpage(request):
    property = Property.objects.all()
    return render(request,'landingpage.html',{'properties': property})


def about(request):
    return render(request,'about.html')


def contact(request):
    return render(request,'contact.html')

from buyer.models import Buyer


def dashboard(request):
    pending_sellers = CustomUser.objects.filter(is_approved=False,is_superuser=False)
    pending_properties = Property.objects.filter(is_approved=False)
    total_sellers = CustomUser.objects.filter(is_superuser=False).count()
    total_properties = Property.objects.count()
    total_buyers = Buyer.objects.filter(is_staff=False).count()
    return render(request, "dashboard.html", {"pending_sellers": pending_sellers,'pending_properties': pending_properties,'total_sellers': total_sellers, 'total_properties': total_properties,'total_buyers': total_buyers})



# Scdeduled Visit
from .models import CustomUser
from buyer.models import VisitSchedule


def visit_requests(request, seller_id):
    seller = get_object_or_404(CustomUser, id=seller_id)
    visits = VisitSchedule.objects.filter(property__seller=seller,status='pending')

    print(f"Seller ID: {seller_id}, Visits Count: {visits.count()}")  # Debugging line
    return render(request, 'visit_requests.html', {'visits': visits, 'seller': seller})


def approve_visit(request, visit_id):
    visit = get_object_or_404(VisitSchedule, id=visit_id)
    visit.status = 'approved'
    visit.is_notified = True
    visit.save()
    # Redirect to seller visit request page or wherever appropriate
    return redirect('visit_requests', seller_id=visit.property.seller.id)


def decline_visit(request, seller_id, visit_id):
    seller = get_object_or_404(CustomUser, id=seller_id)
    visit = get_object_or_404(VisitSchedule, id=visit_id, property__seller=seller)

    visit.status = 'declined'
    visit.save()

    return redirect('visit_requests', seller_id=seller.id)



from buyer.models import Message, VisitSchedule
from django.shortcuts import get_object_or_404, redirect, render

def chat_with_buyer(request, visit_id, sender_type, sender_id):
    visit = get_object_or_404(VisitSchedule, id=visit_id)

    if visit.status != 'approved':
        return render(request, 'chat/invalid_sender.html', {'message': 'Visit not approved.'})

    messages = Message.objects.filter(visit=visit).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')

        if not content:
            return render(request, 'chat.html', {
                'visit': visit,
                'messages': messages,
                'sender_type': sender_type,
                'sender_id': sender_id,
                'error': 'Message cannot be empty.'
            })

        msg_data = {
            'visit': visit,
            'content': content
        }

        if sender_type == 'seller':
            sender = get_object_or_404(CustomUser, id=sender_id)
            msg_data['sender_seller'] = sender
        else:
            return render(request, 'chat/invalid_sender.html', {'message': 'Invalid sender.'})

        Message.objects.create(**msg_data)
        return redirect('seller_chat', visit_id=visit.id, sender_type='seller', sender_id=sender_id)

    return render(request, 'seller_chat.html', {
        'visit': visit,
        'messages': messages,
        'sender_type': 'seller',
        'sender_id': sender_id,
    })

from buyer.models import RentRequest


def pending_rent_requests(request, seller_id):
    seller = get_object_or_404(CustomUser, id=seller_id)
    properties = Property.objects.filter(seller=seller)
    rent_requests = RentRequest.objects.filter(property__in=properties, status='pending')

    return render(request, 'seller_rent_request.html', {
        'rent_requests': rent_requests,
        'seller': seller
    })
def approve_rent_request(request, request_id):
    rent_request = get_object_or_404(RentRequest, id=request_id)
    rent_request.status = 'approved'
    rent_request.save()
    return redirect('seller_rent_requests', seller_id=rent_request.property.seller.id)

def decline_rent_request(request, request_id):
    rent_request = get_object_or_404(RentRequest, id=request_id)
    rent_request.status = 'rejected'
    rent_request.save()
    return redirect('seller_rent_requests', seller_id=rent_request.property.seller.id)