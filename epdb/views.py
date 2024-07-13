import json
import os
import shutil
import uuid
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
from io import BytesIO
import zipfile
from django.http import HttpResponse
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
        gridsize = request.data.get('gridsize')
        gridcenter = request.data.get('gridcenter')

        # Gerar um identificador único para o diretório de upload
        uiddirsave = uuid.uuid4().hex

        # Criação da instância do modelo diretamente
        epdb = EpdbEnergy(
            nome_proces=nome_proces,
            gridsize=gridsize,
            gridcenter=gridcenter
        )
        epdb.set_uiddirsave(uiddirsave)
        epdb.ligand_file = ligand_file
        epdb.receptor_file = receptor_file
        
        epdb.save()

        work_dir = os.path.dirname(epdb.ligand_file.path)
        data_out = process_epdb(epdb)

        # Criação do arquivo zip
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for foldername, subfolders, filenames in os.walk(work_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, work_dir)
                    zip_file.write(file_path, arcname)
            
            # Adicionando data_out como arquivo JSON no zip
            data_out_file_path = os.path.join(work_dir, 'data_out.json')
            with open(data_out_file_path, 'w') as f:
                json.dump(data_out, f)
            zip_file.write(data_out_file_path, 'data_out.json')

        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={nome_proces}.zip'

        # Exclusão de todos os arquivos e diretório após o envio da resposta
        shutil.rmtree(work_dir)
        
        return response