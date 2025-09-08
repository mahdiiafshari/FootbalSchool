from rest_framework.routers import DefaultRouter
from .views import CoachViewSet

router = DefaultRouter()
router.register("coaches", CoachViewSet, basename="coach")

urlpatterns = router.urls
