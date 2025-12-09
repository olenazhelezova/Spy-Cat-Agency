from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CatViewSet, MissionViewSet, TargetViewSet

router = DefaultRouter()
router.register(r'cats', CatViewSet)
router.register(r'missions', MissionViewSet)

embedded_routes = [
    path('missions/<int:mission_pk>/targets/<int:pk>',
         TargetViewSet.as_view({'patch': 'partial_update'}),
         name='mission-target-detail')
]

urlpatterns = router.urls + embedded_routes
