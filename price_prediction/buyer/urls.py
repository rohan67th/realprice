from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('buyer_login/',views.buyer_login,name='buyer_login'),
    path('buyer_registration/',views.buyer_registration,name='buyer_registration'),
    path('buyer_profile/<int:user_id>/',views.buyer_profile,name='buyer_profile'),
    path('seller_logout/',views.seller_logout,name='seller_logout'),
    path('edit_profile_buyer/<int:user_id>/', views.edit_profile_buyer, name='edit_profile_buyer'),
    path('buyer_landing/', views.buyer_landing, name='buyer_landing'),
    path('buyer/<int:buyer_id>/property/<int:pk>/', views.property_detail_buyer, name='property_detail_buyer'),
    path('interest/<int:property_id>/', views.show_interest, name='show_interest'),

    path('predict-price/', views.price_prediction_view, name='predict_price'),

    path('buyer/<int:buyer_id>/property/<int:property_id>/schedule/', views.schedule_visit, name='schedule_visit'),

    path('visit-success/', views.visit_success, name='visit_success'),


    #notifications
    path('buyer/<int:buyer_id>/notifications/', views.buyer_notifications, name='buyer_notifications'),


    #chat

    path('<int:visit_id>/<str:sender_type>/<int:sender_id>/', views.chat_view, name='chat'),



    #complaints
    path('buyer/property/<int:property_id>/complaint/<int:buyer_id>/', views.submit_complaint, name='submit_complaint'),
    path('buyer/<int:buyer_id>/complaints/', views.buyer_complaints, name='buyer_complaints'),



    #Rent
    path('rent/property/<int:property_id>/send/<int:buyer_id>/', views.send_rent_request, name='send_rent_request'),

    

    

    #Forget password

    path('forgot-password/', views.forget_password_buyer, name='forgot-password-buyer'),
    path('password-reset-sent/<str:reset_id>/', views.password_reset_sent_buyer, name='password-reset-sent-buyer'),
    path('reset-password/<str:reset_id>/', views.reset_password_buyer, name='reset-password-buyer'),


    #price prediction 10 years
    path('predict/price/<int:property_id>/', views.predict_price_view, name='predict_price'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 