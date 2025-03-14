import csv
import os
import subprocess
import sys

# Vérifier si le module yaml est installé, sinon l'installer
try:
    import yaml
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

# Chemin relatif du fichier CSV
csv_file_path = os.path.join('..', 'cubiomes', 'build', 'export_markers_dynmap.csv')

# Chemin du fichier YAML
yaml_file_path = os.path.join('plugins', 'dynmap', 'markers.yml')

# Vérifier si le fichier CSV existe
if not os.path.exists(csv_file_path):
    print(f"Le fichier {csv_file_path} n'existe pas.")
else:
    # Lire le fichier CSV
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        
        # Lire les lignes du CSV et les stocker dans une liste
        markers = {}
        for index, row in enumerate(csvreader, start=1):
            marker_id = f"marker_{index}"
            label_id = f"{row['structureType']} {index}"
            markers[marker_id] = {
                'world': 'sandbox',
                'markup': False,
                'x': float(row['x']),
                'icon': row['icon'],
                'y': 64.0,
                'z': float(row['z']),
                'label': label_id
            }
    
    # Charger le fichier YAML existant
    if os.path.exists(yaml_file_path):
        with open(yaml_file_path, 'r', encoding='utf-8') as yamlfile:
            yaml_data = yaml.safe_load(yamlfile)
    else:
        print(f"Le fichier {yaml_file_path} n'existe pas !")
        sys.exit(1)
    
    # Remplacer les anciens marqueurs par les nouveaux
    yaml_data['sets']['markers']['markers'] = markers
    
    # Écrire les données mises à jour dans le fichier YAML
    with open(yaml_file_path, 'w', encoding='utf-8') as yamlfile:
        yamlfile.write('%YAML 1.1\n---\n')
        yaml.safe_dump(yaml_data, yamlfile, default_flow_style=False, allow_unicode=True)