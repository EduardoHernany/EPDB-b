from django.db import models
import uuid

def docking_directory_path(instance, filename):
    uiddirsave = getattr(instance, '_uiddirsave', 'default')
    return 'docking/{0}/{1}'.format(uiddirsave, filename)

class EpdbEnergy(models.Model):
    nome_proces = models.CharField(max_length=200)
    ligand_file = models.FileField(upload_to=docking_directory_path)
    receptor_file = models.FileField(upload_to=docking_directory_path)
    gridsize = models.CharField(max_length=200, blank=True)
    gridcenter = models.CharField(max_length=200, blank=True)
    _uiddirsave = None

    def set_uiddirsave(self, uiddirsave):
        self._uiddirsave = uiddirsave
