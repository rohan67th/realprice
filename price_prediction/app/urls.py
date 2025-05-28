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
    path('property_list/', views.property_list, name='property_list'),
    path('add_property/', views.add_property, name='add_property'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('seller_properties/', views.seller_property_list, name='seller_property_list'),
    path('seller_properties/edit/<int:id>/', views.seller_edit_property, name='seller_edit_property'),
    path('seller_properties/delete/<int:id>/', views.seller_delete_property, name='seller_delete_property'),
    path('seller_pending-properties/', views.seller_pending_properties, name='seller_pending_properties'),





    #admin
    path('admin_login/',views.admin_login,name='admin_login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('approve_seller/<int:seller_id>/', views.approve_seller, name='approve_seller'),
    path('decline_seller/<int:seller_id>/', views.decline_seller, name='decline_seller'),
    path('seller_list/', views.seller_list, name='seller_list'),
    path('toggle-block/<int:user_id>/', views.toggle_block_user, name='toggle_block_user'),
    path('property/<int:property_id>/approve/', views.approve_property, name='approve_property'),
    path('property/<int:property_id>/decline/', views.decline_property, name='decline_property'),
    path('properties/', views.admin_property_list, name='admin_property_list')





] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)