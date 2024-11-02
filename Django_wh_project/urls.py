from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventory import views

router = DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'warehouse', views.WarehouseViewSet)
router.register(r'product', views.ProductViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', views.CustomObtainAuthToken.as_view(), name='api_auth_token'),
    path('api-logout/', views.LogoutView.as_view(), name='logout'),
]
