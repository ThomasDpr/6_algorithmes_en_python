def format_currency(value: float) -> str:
    """Formate un nombre en devise avec le symbole €."""
    return f"{value:.2f}€"

def format_percentage(value: float) -> str:
    """Formate un nombre en pourcentage."""
    return f"{value:.2f}%"

def format_memory(value: float) -> str:
    """Formate une valeur de mémoire en MB."""
    return f"{value:.2f} MB"

def format_time(value: float) -> str:
    """Formate une durée en secondes."""
    return f"{value:.2f} s"