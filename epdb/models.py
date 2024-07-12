from django.db import models

# Create your models here.
def docking_directory_path(instance, filename):
    path = 'docking/{0}/{1}'.format(instance.nome_proces, filename)
    return path

class EpdbEnergy(models.Model):
    nome_proces = models.CharField(max_length=200)
    ligand_file = models.FileField(upload_to=docking_directory_path)
    receptor_file = models.FileField(upload_to=docking_directory_path)
    gridsize = models.CharField(max_length=200,blank=True)
    gridcenter = models.CharField(max_length=200,blank=True)
