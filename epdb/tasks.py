import shutil
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
import subprocess
import os
from pathlib import Path

from epdb.models import EpdbEnergy
from epdb.modules.epd_proces import process_epdb


from .subprocess_tools import execute_command

from celery.utils.log import get_task_logger

# Create a logger instance for this module
logger = get_task_logger(__name__)

# Get a logger for this module

# Define paths to tools and scripts
pythonsh_path = os.path.expanduser("/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/bin/pythonsh")
prep_receptor_path = os.path.expanduser("/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py")
prep_ligand_path = os.path.expanduser("/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_ligand4.py")
prep_gpf_path = os.path.expanduser("/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf4.py")
autogrid_path = os.path.expanduser("/home/autodockgpu/x86_64Linux2/autogrid4")
autodockgpu_path = os.path.expanduser("/home/autodockgpu/AutoDock-GPU/bin/autodock_gpu_128wi")
obabel_path = os.path.expanduser("/home/autodockgpu/build/bin/obabel")
ad4_parameters_path = os.path.expanduser("/var/www/server/AD4_parameters.dat")

@shared_task
def run_epd(epd_id):
    try:
        print(f"Starting the docking process for EPDB ID: {epd_id}")
        epdb = EpdbEnergy.objects.get(id=epd_id)
        process_epdb(epdb)
        
        # # Retrieve the Docking object by ID
        # print(f"Retrieved docking object: {docking.nome_proces}")

        # # Determine the working directory and ensure output directory exists
        # ligand_file_path = docking.ligand_file.path
        # receptor_file_path = docking.receptor_file.path
        # work_dir = os.path.dirname(ligand_file_path)
        # output_dir = os.path.join(settings.MEDIA_ROOT, "docking", docking.nome_proces)
        # os.makedirs(output_dir, exist_ok=True)
        # print(f"Output directory created at {output_dir}")

        # # Prepare ligand
        # ligand_output_path = os.path.splitext(ligand_file_path)[0] + ".pdbqt"
        # print("Preparing ligand...")
        # execute_command([pythonsh_path, prep_ligand_path, '-l', ligand_file_path, '-o', ligand_output_path], cwd=work_dir)
        # print("Ligand preparation completed.")

        # # Prepare receptor
        # receptor_output_path = os.path.splitext(receptor_file_path)[0] + ".pdbqt"
        # print("Preparing receptor...")
        # execute_command([pythonsh_path, prep_receptor_path, '-r', receptor_file_path, '-o', receptor_output_path], cwd=work_dir)
        # print("Receptor preparation completed.")

        # # Prepare grid parameter file
        # output_gpf = os.path.join(output_dir, 'gridbox.gpf')
        # gridcenter = f'gridcenter={docking.gridcenter}'
        # gridsize = f'npts={docking.gridsize}'
        # print("Preparing grid parameter file (GPF)...")
        # gpf_command = [
        #     pythonsh_path, 
        #     prep_gpf_path, 
        #     "-r", receptor_output_path, 
        #     "-l", ligand_output_path, 
        #     "-o", output_gpf, 
        #     "-p", gridcenter, 
        #     "-p", gridsize
        # ]
        # execute_command(gpf_command, cwd=work_dir)
        # print("GPF preparation completed.")

        # # Run AutoGrid
        # print("Running AutoGrid...")
        # sed_command = f"sed -i '1i\\parameter_file {os.path.abspath(ad4_parameters_path)}' {output_gpf}"
        # execute_command(sed_command, shell=True, cwd=output_dir)
        # autogrid_command = [autogrid_path, '-p', output_gpf, "-l", output_gpf.replace('.gpf', '.glg')]
        # execute_command(autogrid_command, cwd=output_dir)
        # print("AutoGrid completed.")

        # # Run AutoDock-GPU
        # fld_file_path = os.path.join(output_dir, f'{Path(receptor_file_path).stem}.maps.fld')
        # print("Running AutoDock-GPU...")
        # autodock_command = [autodockgpu_path, '--ffile', fld_file_path, '--lfile', ligand_output_path]
        # execute_command(autodock_command, cwd=output_dir)
        # print("AutoDock-GPU docking process completed successfully.")

        return "Docking process completed successfully"
    except ObjectDoesNotExist:
        error_message = f"No Docking object found with ID: {epd_id}"
        logger.error(error_message)
        return error_message
    except Exception as e:
        logger.exception("An unexpected error occurred during the docking process.")
        return str(e)
    