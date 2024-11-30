import csv
from typing import List, Tuple

import pandas as pd

from models.action import Action


def load_actions(file_path: str) -> Tuple[List[Action], List[Tuple[Action, List[str]]], List[str]]:
    """
    Charge et valide les actions depuis un fichier CSV.
    Retourne une liste d'actions valides, une liste de tuples d'actions invalides avec leurs raisons,
    et une liste d'erreurs de chargement.
    """
    valid_actions = []
    invalid_actions = []
    errors = []

    try:

        data = pd.read_csv(file_path, header=0)
        
        # Note pandas :
        # La propriété .shape() renvoie le tuple représentant la forme du DataFrame. 
        # [0] représente le nombre de lignes 
        # [1] représente le nombre de colonnes.
        # ex. : data.shape -> (10, 3)
    
        if data.shape[1] < 3:
            raise ValueError("Le fichier CSV doit contenir au moins trois colonnes : nom, coût, et bénéfice.")

        for _, row in data.iterrows():
            try:
                name = row.iloc[0].strip()
                cost = float(row.iloc[1])
                benefit_percent = float(str(row.iloc[2]).strip('%'))

                action = Action(name, cost, benefit_percent)
                if action.is_valid():
                    valid_actions.append(action)
                else:
                    reasons = action.get_invalid_reasons()
                    invalid_actions.append((action, reasons))
            
            except ValueError as e:
                errors.append(f"Erreur de conversion pour {name}: {e}")

    except FileNotFoundError:
        errors.append(f"Le fichier {file_path} n'a pas été trouvé.")
    except Exception as e:
        errors.append(f"Erreur lors de la lecture du fichier: {str(e)}")

    return valid_actions, invalid_actions, errors