
import os
from pathlib import Path
import re
import shutil
import subprocess

from apiTCC import settings
from epdb.subprocess_tools import execute_command

pythonsh_path = os.path.expanduser("/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/bin/pythonsh")
prep_receptor_path = os.path.expanduser("/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_receptor4.py")
prep_ligand_path = os.path.expanduser("/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_ligand4.py")
prep_gpf_path = os.path.expanduser("/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_gpf4.py")
prep_dpf_path = os.path.expanduser("/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/MGLToolsPckgs/AutoDockTools/Utilities24/prepare_dpf4.py")
autogrid_path = os.path.expanduser("/home/autodockgpu/x86_64Linux2/autogrid4")
autoodock_path = os.path.expanduser("/home/autodockgpu/x86_64Linux2/autodock4")
autodockgpu_path = os.path.expanduser("/home/autodockgpu/AutoDock-GPU/bin/autodock_gpu_128wi")
obabel_path = os.path.expanduser("/home/autodockgpu/build/bin/obabel")
ad4_parameters_path = os.path.expanduser("/var/www/server/AD4_parameters.dat")

#/home/eduardo/x86_64Linux2/autodock4 -p 100625391_7tbc_a.dpf -l scoring_result.log


def process_epdb(epdb_instance):
    """
    Orchestrates the virtual screening process for a given screening object.
    
    Args:
        screening (VirtualScreening): An instance of VirtualScreening containing all necessary data.
    """
    ligand_file_path = epdb_instance.ligand_file.path
    receptor_file_path = epdb_instance.receptor_file.path
    work_dir = os.path.dirname(ligand_file_path)
    output_dir = os.path.join(settings.MEDIA_ROOT, "docking", epdb_instance.nome_proces)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory created at {output_dir}")
    
    # # Prepare ligand
    ligand_output_path = os.path.splitext(ligand_file_path)[0] + ".pdbqt"
    print("Preparing ligand...")
    execute_command([pythonsh_path, prep_ligand_path, '-l', ligand_file_path, '-o', ligand_output_path], cwd=work_dir)
    print("Ligand preparation completed.")

    # Prepare receptor
    receptor_output_path = os.path.splitext(receptor_file_path)[0] + ".pdbqt"
    print("Preparing receptor...")
    execute_command([pythonsh_path, prep_receptor_path, '-r', receptor_file_path, '-o', receptor_output_path], cwd=work_dir)
    print("Receptor preparation completed.")

    # Prepare grid parameter file
    output_gpf = os.path.join(output_dir, 'gridbox.gpf')
    gridcenter = f'gridcenter={epdb_instance.gridcenter}'
    gridsize = f'npts={epdb_instance.gridsize}'
    print("Preparing grid parameter file (GPF)...")
    gpf_command = [
        pythonsh_path, 
        prep_gpf_path, 
        "-r", receptor_output_path, 
        "-l", ligand_output_path, 
        "-o", output_gpf, 
        "-p", gridcenter, 
        "-p", gridsize
    ]
    execute_command(gpf_command, cwd=work_dir)
    print("GPF preparation completed.")        
    
    # Run AutoGrid
    print("Running AutoGrid...")
    sed_command = f"sed -i '1i\\parameter_file {os.path.abspath(ad4_parameters_path)}' {output_gpf}"
    execute_command(sed_command, shell=True, cwd=output_dir)
    autogrid_command = [autogrid_path, '-p', output_gpf, "-l", output_gpf.replace('.gpf', '.glg')]
    execute_command(autogrid_command, cwd=output_dir)
    print("AutoGrid completed.")
    
    print("Preparing arquivo DPF...")
    dpf_command = [
        pythonsh_path, 
        prep_dpf_path, 
        "-l", ligand_output_path, 
        "-r", receptor_output_path
    ]
    execute_command(dpf_command, cwd=work_dir)
    print("DPF preparation completed.")
    
    dpf_output = os.path.join(output_dir, f'{Path(ligand_file_path).stem}_{Path(receptor_file_path).stem}.dpf')
    with open(dpf_output, 'r') as file:
        lines = file.readlines()

    # Define up to which line content should be retained
    line_number = 14
    if len(lines) >= line_number:
        with open(dpf_output, 'w') as file:
            file.writelines(lines[:line_number])
            
    with open(dpf_output, 'a') as file:
        file.write('epdb')
    
    print("DPF file modified successfully.")
    
    print("Executando Autodock para epdb...")
    epdb_command = [
        autoodock_path,
        "-p", dpf_output,
        "-l", "scoring_result.log"
    ]
    execute_command(epdb_command, cwd=work_dir)
    print("Autodock para epdb executado com sucesso.")  
    
   # Extrair dados do arquivo scoring_result.log
    scoring_log_path = os.path.join(output_dir, "scoring_result.log")
    with open(scoring_log_path, 'r') as file:
        log_content = file.read()

    # Extrair dados do arquivo scoring_result.log
    scoring_log_path = os.path.join(output_dir, "scoring_result.log")
    with open(scoring_log_path, 'r') as file:
        log_content = file.read()

    # Definir regex para extrair os valores desejados
    patterns = {
        'Estimated Free Energy of Binding': r'Estimated Free Energy of Binding\s*=\s*([+-]?\d+\.?\d*(?:e[+-]?\d+)?\s*kcal/mol)',
        'Final Intermolecular Energy': r'Final Intermolecular Energy\s*=\s*([+-]?\d+\.?\d*(?:e[+-]?\d+)?\s*kcal/mol)',
        'vdW \+ Hbond \+ desolv Energy': r'vdW \+ Hbond \+ desolv Energy\s*=\s*([+-]?\d+\.?\d*(?:e[+-]?\d+)?\s*kcal/mol)',
        'Electrostatic Energy': r'Electrostatic Energy\s*=\s*([+-]?\d+\.?\d*(?:e[+-]?\d+)?\s*kcal/mol)',
        'Final Total Internal Energy': r'Final Total Internal Energy\s*=\s*([+-]?\d+\.?\d*(?:e[+-]?\d+)?\s*kcal/mol)',
        'Torsional Free Energy': r'Torsional Free Energy\s*=\s*([+-]?\d+\.?\d*(?:e[+-]?\d+)?\s*kcal/mol)',
        "Unbound System's Energy": r"Unbound System's Energy\s*=\s*([+-]?\d+\.?\d*(?:e[+-]?\d+)?\s*kcal/mol)",
    }

    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, log_content)
        if match:
            extracted_data[key] = match.group(1)

    # Salvar os dados extraídos em um arquivo
    output_data_path = os.path.join(output_dir, "extracted_data.txt")
    with open(output_data_path, 'w') as file:
        for key, value in extracted_data.items():
            file.write(f"{key}: {value}\n")

    print(f"Dados extraídos salvos em {output_data_path}")