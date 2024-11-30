"""
Classe Action représentant une action d'investissement avec ses méthodes de calcul 
et de validation associées.
"""

from typing import List


class Action:

    # Initialisation
    def __init__(self, name: str, cost: float, benefit_percent: float):
        """Initialise une action avec son nom, coût et pourcentage de bénéfice."""
        self.name = name
        self.cost = cost
        self.benefit_percent = benefit_percent
        self.benefit = self.calculate_benefit()
        self.ratio = self.benefit / self.cost if self.cost > 0 else 0

    # Méthodes de calcul individuelles
    def calculate_cost(self) -> float:
        """Retourne le coût de l'action."""
        return self.cost
    
    def calculate_benefit(self) -> float:
        """Calcule le bénéfice en euros basé sur le pourcentage."""
        return (self.cost * self.benefit_percent) / 100.0

    # Méthodes de validation individuelles
    def is_valid(self) -> bool:
        """Vérifie la validité de l'action selon les critères établis."""
        try:
            if not isinstance(self.cost, (int, float)) or not isinstance(self.benefit_percent, (int, float)):
                return False
            return self.cost > 0 and self.benefit_percent > 0
        except (TypeError, ValueError):
            return False

    def get_invalid_reasons(self) -> list[str]:
        """Liste les raisons de l'invalidité de l'action."""
        reasons = []
        
        if not isinstance(self.cost, (int, float)) or not isinstance(self.benefit_percent, (int, float)):
            return ["Format invalide"]
        
        if self.cost <= 0:
            reasons.append("Coût <= 0")
        if self.benefit_percent <= 0:
            reasons.append("Bénéfice % <= 0")
            
        return reasons


    # Méthodes de calcul pour portefeuille
    @staticmethod
    def total_portfolio_cost(actions: List['Action']) -> float:
        """Calcule le coût total d'un portefeuille d'actions."""
        return sum(action.calculate_cost() for action in actions)

    @staticmethod
    def total_portfolio_benefit(actions: List['Action']) -> float:
        """Calcule le bénéfice total d'un portefeuille d'actions."""
        return sum(action.calculate_benefit() for action in actions)

    @staticmethod
    def is_portfolio_within_budget(actions: List['Action'], max_budget: float) -> bool:
        """Vérifie si le portefeuille respecte le budget maximum."""
        return Action.total_portfolio_cost(actions) <= max_budget

    # Représentation
    def __str__(self) -> str:
        """Représentation textuelle de l'action."""
        return f"{self.name} (Coût: {self.cost}€, Bénéfice: {self.benefit_percent}%)"
    def __repr__(self) -> str:
        """Représentation plus détaillée pour le débogage."""
        return f"Action(name={self.name}, cost={self.cost}, benefit_percent={self.benefit_percent})"