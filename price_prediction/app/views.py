from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser,PasswordReset
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse,StreamingHttpResponse



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


def approve_seller(request, seller_id):
    seller = get_object_or_404(CustomUser, id=seller_id)
    seller.is_approved = True
    seller.save()
    return redirect('dashboard')

def decline_seller(request, seller_id):
    seller = get_object_or_404(CustomUser, id=seller_id)
    seller.delete()
    return redirect('dashboard')


def seller_list(request):
    users = CustomUser.objects.filter(is_approved=True, is_superuser=False)
    return render(request, 'seller_list.html', {'users': users})


def toggle_block_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    return redirect('seller_list')

#Seller

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

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
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


def seller_profile(request,user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'seller_profile.html', {'user': user})





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
    return render(request,'landingpage.html')


def about(request):
    return render(request,'about.html')


def contact(request):
    return render(request,'contact.html')


def dashboard(request):
    pending_sellers = CustomUser.objects.filter(is_approved=False,is_superuser=False)
    return render(request, "dashboard.html", {"pending_sellers": pending_sellers})