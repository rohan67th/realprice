from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('buyer_login/',views.buyer_login,name='buyer_login'),
    path('buyer_registration/',views.buyer_registration,name='buyer_registration'),
    path('buyer_profile/<int:user_id>/',views.buyer_profile,name='buyer_profile'),
    path('seller_logout/',views.seller_logout,name='seller_logout'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 