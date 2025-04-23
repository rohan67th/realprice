from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .models import Buyer
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth import logout

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



def edit_profile(request):
    user = Buyer.objects.get(email=request.user.email)

    if request.method == 'POST':
        user.name = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        user.gender = request.POST.get('gender')

        # Handle profile picture if uploaded
        if 'profile_pic' in request.FILES:
            user.profile_pic = request.FILES['profile_pic']

        user.save()

        messages.success(request, "Profile updated successfully!")
        profile_url = reverse('seller_profile', kwargs={'user_id': user.id})
        return redirect(profile_url)

    return render(request, 'edit_seller.html', {'user': user})