from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import Buyer,PasswordResetBuyer
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth import logout
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponseRedirect


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
            return redirect('buyer_login')  # Redirect to the login page

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
            profile_url = reverse('buyer_profile', kwargs={'user_id': buyer.id})
            return redirect(profile_url)
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'buyer_login.html')




def buyer_profile(request,user_id):
    buyer = get_object_or_404(Buyer, id=user_id)
    return render(request, 'buyer_profile.html', {'buyer': buyer})


def seller_logout(request):
    logout(request)
    return redirect('/')



def edit_profile_buyer(request):

    buyer = request.session.get('id')
    print(buyer)

    if request.method == 'POST':
        buyer.name = request.POST.get('name')
        buyer.email = request.POST.get('email')
        buyer.phone = request.POST.get('phone')
        buyer.address = request.POST.get('address')
        buyer.gender = request.POST.get('gender')

        # Handle profile picture if uploaded
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