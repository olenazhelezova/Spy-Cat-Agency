from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from .models import Cat, Mission, Target
from .serializers import CatSerializer, MissionSerializer, TargetSerializer
from drf_spectacular.utils import extend_schema_serializer, extend_schema


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = [AllowAny]


#Dirty hack for openapi generation hinting
@extend_schema_serializer(exclude_fields=("is_complete", "targets"))
class MissionUpdateSchemaHack(MissionSerializer):
    pass


class MissionViewSet(viewsets.ModelViewSet):
    """
    Handles Mission CRUD and agency business logic for assignments and completion.
    """
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    def perform_destroy(self, instance):
        if instance.cat is not None:
            raise ValidationError(
                {"detail": "Cannot abort the mission, cat is already in the field"})
        instance.delete()

    # Dirty hacks for openapi generation hinting

    @extend_schema(
        request=MissionUpdateSchemaHack,
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        request=MissionUpdateSchemaHack,
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class TargetViewSet(viewsets.ModelViewSet):
    serializer_class = TargetSerializer

    def get_queryset(self):
        mission_id = self.kwargs["mission_pk"]

        return Target.objects.filter(mission_id=mission_id)
