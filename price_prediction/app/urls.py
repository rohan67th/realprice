from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('',views.landingpage,name='landingpage'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),


    #seller
    path('register/',views.seller_register,name='register'),
    path('login/',views.seller_login,name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('seller_profile/<int:user_id>/', views.seller_profile, name='seller_profile'),
    path('forgot-password/', views.forget_password, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.password_reset_sent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.reset_password, name='reset-password'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),





    #admin
    path('admin_login/',views.admin_login,name='admin_login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('approve_seller/<int:seller_id>/', views.approve_seller, name='approve_seller'),
    path('decline_seller/<int:seller_id>/', views.decline_seller, name='decline_seller'),
    path('seller_list/', views.seller_list, name='seller_list'),
    path('toggle-block/<int:user_id>/', views.toggle_block_user, name='toggle_block_user'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)