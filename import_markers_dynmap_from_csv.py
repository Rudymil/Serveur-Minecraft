import csv
import os
import subprocess
import sys

# Vérifier si les modules nécessaires sont installés, sinon les installer
try:
    import yaml
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

try:
    import inflect
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "inflect"])
    import inflect

# Initialiser l'objet inflect pour gérer les pluriels
p = inflect.engine()

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
        
        # Charger le fichier YAML existant
        if os.path.exists(yaml_file_path):
            with open(yaml_file_path, 'r', encoding='utf-8') as yamlfile:
                yaml_data = yaml.safe_load(yamlfile)
        else:
            print(f"Le fichier {yaml_file_path} n'existe pas !")
            sys.exit(1)
        
        # Supprimer toutes les balises dans 'sets' sauf 'spawn_beds', 'offline_players' et 'markers'
        keys_to_keep = ['spawn_beds', 'offline_players', 'markers']
        yaml_data['sets'] = {key: yaml_data['sets'][key] for key in keys_to_keep if key in yaml_data['sets']}
        
        # S'assurer que les balises 'spawn_beds', 'offline_players' et 'markers' existent et que leur valeur 'hide' est False
        for key in ['spawn_beds', 'offline_players', 'markers']:
            if key in yaml_data['sets']:
                yaml_data['sets'][key]['hide'] = False

        # Initialiser la structure si nécessaire
        if 'sets' not in yaml_data:
            yaml_data['sets'] = {}

        # Lire les lignes du CSV et les stocker dans la structure YAML
        for index, row in enumerate(csvreader, start=1):
            x = float(row['x'])
            z = float(row['z'])

            # Vérifier si les coordonnées sont en dehors des BBOX spécifiées
            if not (
                (-512 <= x <= 512 and 0 <= z <= 1024) or
                (-1024 <= x <= -512 and 512 <= z <= 1024)
            ):
                structure_type = row['structureType']
                structure_type_plural = p.plural(structure_type)  # Convertir en pluriel avec accord grammatical
                marker_id = f"marker_{index}"
                label_id = f"{structure_type} {index}"

                # Initialiser la section pour le type de structure si elle n'existe pas
                if structure_type_plural not in yaml_data['sets']:
                    yaml_data['sets'][structure_type_plural] = {
                        'hide': True,
                        'circles': {},
                        'deficon': 'default',
                        'areas': {},
                        'label': structure_type_plural,
                        'markers': {},
                        'lines': {},
                        'layerprio': 0
                    }
                
                # Ajouter le marqueur à la section correspondante
                yaml_data['sets'][structure_type_plural]['markers'][marker_id] = {
                    'world': 'sandbox',
                    'markup': False,
                    'x': x,
                    'icon': row['icon'],
                    'y': 64.0,
                    'z': z,
                    'label': label_id
                }
    
    # Écrire les données mises à jour dans le fichier YAML
    with open(yaml_file_path, 'w', encoding='utf-8') as yamlfile:
        yamlfile.write('%YAML 1.1\n---\n')
        yaml.safe_dump(yaml_data, yamlfile, default_flow_style=False, allow_unicode=True)