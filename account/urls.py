from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, UserSignupView, UserLoginView, PasswordChangeView

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
]