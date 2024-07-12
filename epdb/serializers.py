from rest_framework import serializers
from .models import EpdbEnergy
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class EpdbEnergyserializer(serializers.ModelSerializer):
    class Meta:
        model = EpdbEnergy
        fields = '__all__'
