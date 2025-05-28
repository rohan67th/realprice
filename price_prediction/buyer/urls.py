from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('buyer_login/',views.buyer_login,name='buyer_login'),
    path('buyer_registration/',views.buyer_registration,name='buyer_registration'),
    path('buyer_profile/<int:user_id>/',views.buyer_profile,name='buyer_profile'),
    path('seller_logout/',views.seller_logout,name='seller_logout'),
    path('edit_profile_buyer/', views.edit_profile_buyer, name='edit_profile_buyer'),


    #Forget password

    path('forgot-password/', views.forget_password_buyer, name='forgot-password-buyer'),
    path('password-reset-sent/<str:reset_id>/', views.password_reset_sent_buyer, name='password-reset-sent-buyer'),
    path('reset-password/<str:reset_id>/', views.reset_password_buyer, name='reset-password-buyer'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 