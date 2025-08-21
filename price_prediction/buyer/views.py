from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages

from app.models import Property
from .models import Buyer,PasswordResetBuyer,BuyerInterest
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth import logout
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponseRedirect
from .models import RentRequest,VisitSchedule


def buyer_registration(request):
    if request.method == "POST":
        # Extract data from the POST request
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        profile_pic = request.FILES.get('profile_pic')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')


        if not name or not email or not phone or not address or not gender or not password:
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        
        try:
            faculty = Buyer(
                name=name,
                email=email,
                phone=phone,
                address=address,
                gender=gender,
                profile_pic=profile_pic
            )
            # Hash the password before saving it
            faculty.set_password(password)
            faculty.save()

            messages.success(request, "Registration successful! You can now log in.")
            return redirect('buyer_login')

        except ValidationError as e:
            messages.error(request, f"Error: {e}")
            return redirect('buyer_registration')

    return render(request, 'buyer_registration.html')



def buyer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            buyer = Buyer.objects.get(name=username)
        except Buyer.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('buyer_login')

        if buyer.check_password(password):
            request.session['buyer_id'] = buyer.id 
            messages.success(request, f"Welcome back, {buyer.name}!")
      
            return redirect('buyer_landing')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'buyer_login.html')


def buyer_landing(request):
    buyer = get_object_or_404(Buyer, id=request.session.get('buyer_id'))
    properties = Property.objects.filter(is_approved=True)  # Fetch all approved properties
    if not buyer:
        messages.error(request, "You need to log in first.")
        return redirect('buyer_login')
    return render(request,'buyer_landing.html',{'buyer': buyer,'properties': properties})

def property_detail_buyer(request,buyer_id, pk):
    property = get_object_or_404(Property, pk=pk)
    buyer = get_object_or_404(Buyer, id=buyer_id)
    complaints = Complaint.objects.filter(property=property).order_by('-created_at')

    return render(request, 'property_detail_buyer.html', {'property': property,'buyer': buyer,'complaints': complaints})


def buyer_profile(request,user_id):
    buyer = get_object_or_404(Buyer, id=user_id)
    return render(request, 'buyer_profile.html', {'buyer': buyer})


def seller_logout(request):
    logout(request)
    return redirect('/')



def edit_profile_buyer(request,user_id):

    buyer = get_object_or_404(Buyer, id=user_id)

    if request.method == 'POST':
        buyer.name = request.POST.get('name')
        buyer.email = request.POST.get('email')
        buyer.phone = request.POST.get('phone')
        buyer.address = request.POST.get('address')
        buyer.gender = request.POST.get('gender')

        if 'profile_pic' in request.FILES:
            buyer.profile_pic = request.FILES['profile_pic']

        buyer.save()

        messages.success(request, "Profile updated successfully!")
        profile_url = reverse('buyer_profile', kwargs={'user_id': buyer.id})
        return redirect(profile_url)

    return render(request, 'edit_buyer.html', {'user': buyer})




#Forget password

from django.utils import timezone

def forget_password_buyer(request):
    
    if request.method =="POST":
        email = request.POST.get('email')

        try:
            user = Buyer.objects.get(email=email)

            new_password_reset = PasswordResetBuyer(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password-buyer', kwargs={'reset_id': new_password_reset.reset_id})

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

            return HttpResponseRedirect(reverse("password-reset-sent-buyer", kwargs={"reset_id": new_password_reset.reset_id}))
        
        except Buyer.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password-buyer')

    return render(request,'forget_password_buyer.html')


def password_reset_sent_buyer(request,reset_id):

    if PasswordResetBuyer.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent_buyer.html')
    else:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password-buyer')


def reset_password_buyer(request,reset_id):
    
    try:
        password_reset_id = PasswordResetBuyer.objects.get(reset_id=reset_id)

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
                return redirect('buyer_login')
            
            else:
                return redirect('reset-password-buyer',reset_id=reset_id)

    
    
    except PasswordResetBuyer.DoesNotExist:
        
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password-buyer')

    return render(request, 'reset_password_buyer.html',{'reset_id': reset_id})



def show_interest(request, property_id):
    if request.method == 'POST':
        property_obj = get_object_or_404(Property, id=property_id)

        buyer = get_object_or_404(Buyer, email=request.user.email)

        interest, created = BuyerInterest.objects.get_or_create(
            buyer=buyer,
            property=property_obj
        )

        if not created:
            messages.info(request, "You've already expressed interest.")
        else:
            messages.success(request, "Your interest has been submitted.")

        return redirect('property_detail', property_id=property_id)








#price prediction

import numpy as np
import joblib
import os



# Load saved scaler and model
scaler_path = os.path.join(settings.BASE_DIR, 'buyer', 'scaler.joblib')
scaler = joblib.load(scaler_path)


model_path = os.path.join(settings.BASE_DIR, 'buyer', 'best_model.joblib')
model = joblib.load(model_path)

# Function to preprocess and predict on new data
def predict_new_data(input_features):
    """
    Predicts house value using pre-trained model.
    
    Parameters:
        input_features (list or array): Must include these 8 raw features in this order:
        [MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude]
        
    Returns:
        Predicted median house value (float)
    """
    if len(input_features) != 8:
        raise ValueError("Expected 8 input features: [MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude]")
    
    # Convert to numpy array
    input_features = np.array(input_features, dtype=float)
    
    # Derived features
    ave_rooms = input_features[2]
    ave_occup = input_features[5]
    
    # Just use an estimated house value for PricePerRoom if MedHouseVal is not known; here we set a dummy average (can be improved)
    estimated_house_value = 200000  # Just for deriving price per room; the real value is being predicted
    price_per_room = estimated_house_value / ave_rooms if ave_rooms != 0 else 0
    rooms_per_household = ave_rooms / ave_occup if ave_occup != 0 else 0
    
    # Combine raw + engineered features
    full_features = np.append(input_features, [price_per_room, rooms_per_household]).reshape(1, -1)
    
    # Scale features
    full_features_scaled = scaler.transform(full_features)
    
    # Predict
    prediction = model.predict(full_features_scaled)[0]
    return prediction

# Example new data input
new_sample = [
    3.5,     # MedInc
    25.0,    # HouseAge
    5.2,     # AveRooms
    2.0,     # AveBedrms
    800,     # Population
    2.2,     # AveOccup
    36.5,    # Latitude
    -121.5   # Longitude
]

# Make prediction
predicted_value = predict_new_data(new_sample)

def price_prediction_view(request):
    if request.method == 'POST':
        try:
            fields = ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude']
            input_features = [float(request.POST.get(field)) for field in fields]

            predicted_price = predict_new_data(input_features)

   
            return render(request, 'prediction_result.html', {'predicted_price': predicted_price})

        except Exception as e:
            return render(request, 'price_predict.html', {'error': str(e)})
    return render(request, 'price_predict.html')





#Schedule a visit
from .models import VisitSchedule

def schedule_visit(request, buyer_id, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    buyer = get_object_or_404(Buyer, id=buyer_id)

    if request.method == "POST":
        scheduled_date = request.POST.get("scheduled_date")
        scheduled_time = request.POST.get("scheduled_time")
        message = request.POST.get("message")

        VisitSchedule.objects.create(
            buyer=buyer,
            property=property_obj,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            message=message,
        )
        return redirect('visit_success')  # Or redirect back to the property page

    return render(request, 'schedule_visit.html', {
        'property': property_obj,
        'buyer': buyer,
    })



def visit_success(request):
    return render(request, 'visit_success.html')


def send_rent_request(request, property_id, buyer_id):
    buyer = get_object_or_404(Buyer, id=buyer_id)
    property_obj = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']

        RentRequest.objects.create(
            property=property_obj,
            buyer=buyer,
            start_date=start_date,
            end_date=end_date
        )
        return redirect('property_detail_buyer',buyer_id=buyer.id, pk=property_obj.id)

    return render(request, 'rent_request.html', {'property': property_obj, 'buyer': buyer})

def rent(request):
    return render(request,'rent_request.html')


#Notifications

def buyer_notifications(request, buyer_id):
    buyer = get_object_or_404(Buyer, id=buyer_id)

    # 1. Visit approvals
    notifications = VisitSchedule.objects.filter(
        buyer=buyer,
        status='approved',
        is_seen_by_buyer=False
    )

    # 2. Rent payments (assuming is_paid=True and not yet seen)
    rent_notifications = RentRequest.objects.filter(
        buyer=buyer,
        status='approved',
        is_paid=True,  # you might already be using this
        is_seen_by_buyer=False
    )

    # 3. Approved/Declined rent request updates (excluding pending)
    approval_notifications = RentRequest.objects.filter(
        buyer=buyer,
    ).exclude(status='pending').order_by('-updated_at')

    return render(request, 'buyer_notifications.html', {
        'buyer': buyer,
        'notifications': notifications,
        'rent_notifications': rent_notifications,
        'approval_notifications': approval_notifications,
    })




# chat

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message, VisitSchedule, Buyer
from app.models import CustomUser


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        visit_id = data['visit_id']
        content = data['content']
        sender_type = data['sender_type']  # 'buyer' or 'seller'

        try:
            visit = VisitSchedule.objects.get(id=visit_id)
        except VisitSchedule.DoesNotExist:
            return JsonResponse({'error': 'Visit not found'}, status=404)

        if visit.status != 'approved':
            return JsonResponse({'error': 'Visit not approved'}, status=403)

        if sender_type == 'buyer':
            sender = Buyer.objects.get(id=data['sender_id'])
            message = Message.objects.create(
                visit=visit,
                sender_buyer=sender,
                content=content
            )
        elif sender_type == 'seller':
            sender = CustomUser.objects.get(id=data['sender_id'])
            message = Message.objects.create(
                visit=visit,
                sender_seller=sender,
                content=content
            )
        else:
            return JsonResponse({'error': 'Invalid sender type'}, status=400)

        return JsonResponse({'success': True, 'message': 'Message sent'})
    

def get_messages(request, visit_id):
    try:
        visit = VisitSchedule.objects.get(id=visit_id)
    except VisitSchedule.DoesNotExist:
        return JsonResponse({'error': 'Visit not found'}, status=404)

    messages = Message.objects.filter(visit=visit).order_by('timestamp')
    message_list = []

    for msg in messages:
        sender_name = (
            msg.sender_buyer.name if msg.sender_buyer
            else msg.sender_seller.name if msg.sender_seller
            else 'Unknown'
        )
        message_list.append({
            'sender': sender_name,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({'messages': message_list})





def chat_view(request, visit_id, sender_type, sender_id):
    visit = get_object_or_404(VisitSchedule, id=visit_id)

    if visit.status != 'approved':
        return render(request, 'chat/not_approved.html')

    if request.method == 'POST':
        content = request.POST.get('content')
        msg_data = {'visit': visit, 'content': content}

        if sender_type == 'buyer':
            buyer = get_object_or_404(Buyer, id=sender_id)
            msg_data['sender_buyer'] = buyer
        elif sender_type == 'seller':
            seller = get_object_or_404(CustomUser, id=sender_id)
            msg_data['sender_seller'] = seller
        else:
            return render(request, 'chat/invalid_sender.html')

        Message.objects.create(**msg_data)
        return redirect('chat', visit_id=visit.id, sender_type=sender_type, sender_id=sender_id)

    messages = visit.chat_messages.order_by('timestamp')

    return render(request, 'chat.html', {
        'visit': visit,
        'messages': messages,
        'sender_type': sender_type,
        'sender_id': sender_id,
        'error': 'Invalid sender type.'
    })


from .models import Complaint

#complaints
def submit_complaint(request, property_id,buyer_id):
    if request.method == 'POST':
        category = request.POST.get('category')
        priority = request.POST.get('priority')
        description = request.POST.get('description')

        property_obj = get_object_or_404(Property, id=property_id)
        buyer = get_object_or_404(Buyer, id=buyer_id)

        Complaint.objects.create(
            property=property_obj,
            buyer=buyer,
            category=category,
            priority=priority,
            description=description
        )

        messages.success(request, 'Your complaint has been submitted successfully.')
        return redirect('property_detail_buyer', buyer_id=buyer_id, pk=property_id)



def buyer_complaints(request, buyer_id):
    buyer = get_object_or_404(Buyer, id=buyer_id)
    complaints = Complaint.objects.filter(buyer=buyer)
    return render(request, 'complaints.html', {'buyer': buyer, 'complaints': complaints})



from .utils import predict_future_price

def predict_price_view(request, property_id):
    try:
        property = Property.objects.get(id=property_id)
        future_price = predict_future_price(property.price)
        return JsonResponse({
            'success': True,
            'current_price': float(property.price),
            'future_price': future_price,
            'years': 10
        })
    except Property.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Property not found'})



