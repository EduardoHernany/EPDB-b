from django.shortcuts import render

from epdb.models import EpdbEnergy
from epdb.modules.epd_proces import process_epdb
from epdb.serializers import EpdbEnergyserializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import views, status
from rest_framework.response import Response

from epdb.tasks import run_epd
# Create your views here.

class DockingView(viewsets.ModelViewSet):
    queryset = EpdbEnergy.objects.all()
    serializer_class = EpdbEnergyserializer
    parser_classes = (MultiPartParser, FormParser)  
    
    receptor_param = openapi.Parameter(
        'receptor_file', in_=openapi.IN_FORM, description="Upload receptor file",
        type=openapi.TYPE_FILE, required=True
    )
    ligand_param = openapi.Parameter(
        'ligand_file', in_=openapi.IN_FORM, description="Upload ligand file",
        type=openapi.TYPE_FILE, required=True
    )
    name_param = openapi.Parameter(
        'nome_proces', in_=openapi.IN_FORM, description="Name of the docking process",
        type=openapi.TYPE_STRING, required=True
    )
    gridsize_param = openapi.Parameter(
        'gridsize', in_=openapi.IN_FORM, description="gridsize_param",
        type=openapi.TYPE_STRING, required=True
    )
    gridcenter_param = openapi.Parameter(
        'gridcenter', in_=openapi.IN_FORM, description="gridcenter_param",
        type=openapi.TYPE_STRING, required=True
    )

    @swagger_auto_schema(
        manual_parameters=[name_param, receptor_param, ligand_param, gridsize_param, gridcenter_param],
        responses={
            202: 'Instância criada com sucesso!',
            400: 'Dados inválidos'
        },
        consumes=['multipart/form-data']  # Important for file uploads
    )
    def create(self, request, *args, **kwargs):
        ligand_file = request.FILES.get('ligand_file')
        receptor_file = request.FILES.get('receptor_file')
        
        if not ligand_file or not receptor_file:
            return Response({'error': 'Missing files'}, status=status.HTTP_400_BAD_REQUEST)
        
        nome_proces = request.data.get('nome_proces')
        if EpdbEnergy.objects.filter(nome_proces=nome_proces).exists():
            return Response({'error': 'A docking process with this name already exists.'}, status=status.HTTP_409_CONFLICT)  
        #----------------TUDO CERTO PARA EXECUÇÂO--------------------------
        data = {
            'nome_proces': request.data.get('nome_proces'),
            'ligand_file': ligand_file,
            'receptor_file': receptor_file,
            'gridsize': request.data.get('gridsize'),
            'gridcenter': request.data.get('gridcenter')
        }
        serializer = EpdbEnergyserializer(data=data) 
        if serializer.is_valid():
            instance = serializer.save()
            # Pass the instance ID to the Celery task
            process_epdb.delay(instance.id)
            return Response({'message': 'Instância criada com sucesso!'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
