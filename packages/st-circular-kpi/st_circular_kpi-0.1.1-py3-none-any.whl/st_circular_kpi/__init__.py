import os
import streamlit.components.v1 as components
from pathlib import Path

_RELEASE = True

component_name = "st_circular_kpi"

if _RELEASE:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component(component_name, path=build_dir)
else:
    _component_func = components.declare_component(component_name, url="http://localhost:3001")



def circular_kpi(
    value: float,
    label: str,
    range: tuple = (0, 100),  # Range du cercle (min_range, max_range)
    min_value: float = None,  # Statistique min (optionnel)
    max_value: float = None,  # Statistique max (optionnel)
    mean_value: float = None, # Statistique mean (optionnel)
    unit: str = "",
    color_scheme: str = "blue_purple",  # blue_purple, green, red, orange
    size: int = 200,
    show_stats: bool = True,
    background_color: str = "transparent",
    key=None
):
    """
    Affiche un KPI circulaire avec statistiques.
    
    Parameters:
    -----------
    value : float
        La valeur principale à afficher
    label : str
        Le nom du KPI
    range : tuple
        Range du cercle (min_range, max_range) - définit l'échelle du cercle
    min_value : float
        Statistique minimum à afficher (optionnel)
    max_value : float
        Statistique maximum à afficher (optionnel)
    mean_value : float
        Statistique moyenne à afficher (optionnel)
    unit : str
        Unité de mesure (%, €, etc.)
    color_scheme : str
        Schéma de couleurs : 'blue_purple', 'green', 'red', 'orange'
    size : int
        Taille du cercle en pixels
    show_stats : bool
        Afficher les statistiques (min, max, mean)
    background_color : str
        Couleur de fond ('transparent' par défaut, ou couleur hex comme '#f0f0f0')
    key : str
        Clé unique pour le composant
    
    Returns:
    --------
    dict
        Les données du composant
    """
    
    # Extraire le range
    min_range, max_range = range
    
    # Calculer le pourcentage basé sur le range
    if max_range > min_range:
        percentage = ((value - min_range) / (max_range - min_range)) * 100
    else:
        percentage = 0
    
    component_value = _component_func(
        value=value,
        label=label,
        min_range=min_range,
        max_range=max_range,
        min_value=min_value,
        max_value=max_value,
        mean_value=mean_value,
        unit=unit,
        color_scheme=color_scheme,
        size=size,
        show_stats=show_stats,
        background_color=background_color,
        percentage=percentage,
        key=key,
        default=None
    )
    
    return component_value