from rest_framework import serializers
from django.db import transaction
from .models import Cat, Mission, Target
from .validators import validate_cat_breed
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer, extend_schema
from rest_framework.fields import IntegerField


class CatSerializer(serializers.ModelSerializer):
    current_mission_id = serializers.SerializerMethodField()
    salary = serializers.FloatField(min_value=0, max_value=1000000)
    years_of_experience = serializers.IntegerField(min_value=0, max_value=20)

    class Meta:
        model = Cat
        fields = ['id', 'name', 'years_of_experience', 'breed',
                  'salary', 'is_available', 'current_mission_id']
        read_only_fields = ['id', 'is_available']

    def validate_breed(self, breed_value):
        validate_cat_breed(breed_value)
        return breed_value

    @extend_schema_field(IntegerField)
    def get_current_mission_id(self, cat_instance):
        return cat_instance.current_mission.pk if cat_instance.current_mission else None


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['id', 'name', 'country', 'notes', 'is_complete']

    def validate(self, data):
        if self.instance is not None and self.instance.is_complete:
            raise serializers.ValidationError(
                "Cannot update completed mission target")
        return data

    @transaction.atomic
    def update(self, instance: Target, validated_data):
        instance = super().update(instance, validated_data)
        mission = instance.mission
        if not mission.targets.filter(is_complete=False):
            mission.is_complete = True
            mission.save()

        return instance


class MissionSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True)

    class Meta:
        model = Mission
        fields = ['id', 'cat', 'is_complete', 'targets']
        read_only_fields = ['id']

    def validate_cat(self, cat):
        if self.instance is not None:
            if self.instance.cat is not None:
                raise serializers.ValidationError(
                    "Cannot reassign mission: current spy cat is deployed")
        
        if cat is not None and cat.is_available == False:
            raise serializers.ValidationError(
                "Cannot assign mission to cat currently in the field")
        return cat

    def validate_targets(self, targets):
        """Rule: Minimum 1, Maximum 3 targets per mission."""
        if not (1 <= len(targets) <= 3):
            raise serializers.ValidationError(
                "Mission must have between 1 and 3 targets.")
        return targets

    def update(self, instance, validated_data):
        # Cleaning up data that shouldn't be modifiable
        IMMUTABLE_FIELDS = ["is_complete", "targets"]
        for field in IMMUTABLE_FIELDS:
            if field in validated_data:
                del validated_data[field]

        return super().update(instance, validated_data)

    @transaction.atomic
    def create(self, validated_data):
        targets_data = validated_data.pop('targets')
        mission = Mission.objects.create(**validated_data)

        Target.objects.bulk_create([
            Target(mission=mission, **target_data) for target_data in targets_data
        ])

        return mission
