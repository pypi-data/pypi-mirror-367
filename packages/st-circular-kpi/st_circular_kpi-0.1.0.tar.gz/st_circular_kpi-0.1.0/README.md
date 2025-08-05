# 🎯 Streamlit Circular KPI

Un composant Streamlit personnalisé pour afficher des indicateurs de performance clés (KPI) sous forme de graphiques circulaires élégants et interactifs.

## ✨ Fonctionnalités

- 📊 **Graphiques circulaires animés** avec dégradés de couleurs
- 📈 **Statistiques visuelles** (Min, Max, Moyenne) positionnées selon leur valeur
- 🎨 **4 schémas de couleurs prédéfinis** (bleu-violet, vert, rouge, orange)
- 🔧 **Hautement personnalisable** (taille, couleurs, unités, etc.)
- 📱 **Responsive** et adapté aux layouts Streamlit
- 🖱️ **Interactif** avec callbacks de clic
- 🎯 **Police Urbanist** pour un design moderne

## 🚀 Installation

```bash
pip install st-circular-kpi
```

## 📋 Démarrage rapide

```python
import streamlit as st
from st_circular_kpi import circular_kpi

st.title("Mon Dashboard KPI")

# KPI simple
result = circular_kpi(
    value=85,
    label="Performance",
    unit="%",
    color_scheme="blue_purple"
)
```

## 🎨 Exemples d'utilisation

### KPI avec statistiques complètes

```python
circular_kpi(
    value=80,                    # Valeur principale
    label="Performance", 
    range=(0, 100),             # Range du cercle [0-100]
    min_value=50,               # Minimum affiché
    max_value=90,               # Maximum affiché
    mean_value=70,              # Moyenne affichée
    unit="%",
    color_scheme="blue_purple",
    size=200,
    background_color="transparent",
    key="perf"
)
```

### Différents KPI en colonnes

```python
col1, col2, col3, col4 = st.columns(4)

with col1:
    circular_kpi(
        value=1250,
        label="Ventes",
        range=(0, 2000),
        mean_value=1100,
        unit="€",
        color_scheme="green",
        key="sales"
    )

with col2:
    circular_kpi(
        value=12,
        label="Erreurs",
        range=(0, 50),
        mean_value=25,
        color_scheme="red",
        key="errors"
    )

with col3:
    circular_kpi(
        value=4.2,
        label="Satisfaction",
        range=(1, 5),
        mean_value=3.8,
        unit="/5",
        color_scheme="orange",
        key="satisfaction"
    )
```

## 🔧 API de référence

### Paramètres

| Paramètre | Type | Défaut | Description |
|-----------|------|---------|-------------|
| `value` | `float` | `80` | Valeur principale du KPI |
| `label` | `str` | `"KPI"` | Libellé affiché sous la valeur |
| `range` | `tuple` | `(0, 100)` | Range min/max pour les calculs d'angles |
| `min_value` | `float` | `None` | Valeur minimale à afficher |
| `max_value` | `float` | `None` | Valeur maximale à afficher |
| `mean_value` | `float` | `None` | Valeur moyenne à afficher |
| `unit` | `str` | `""` | Unité affichée après la valeur |
| `color_scheme` | `str` | `"blue_purple"` | Schéma de couleurs |
| `size` | `int` | `200` | Taille du composant en pixels |
| `show_stats` | `bool` | `True` | Afficher/masquer les statistiques |
| `background_color` | `str` | `"transparent"` | Couleur de fond |
| `percentage` | `float` | `80` | Pourcentage de remplissage de l'arc |
| `key` | `str` | `None` | Clé unique pour Streamlit |

### Schémas de couleurs disponibles

- `"blue_purple"` : Dégradé bleu vers violet
- `"green"` : Tons de vert
- `"red"` : Tons de rouge  
- `"orange"` : Tons d'orange

### Valeur de retour

Le composant retourne un dictionnaire contenant :
```python
{
    "value": 80,
    "label": "Performance", 
    "percentage": 80,
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 🎨 Personnalisation avancée

### Couleurs personnalisées

Pour ajouter vos propres schémas de couleurs, modifiez le fichier `CustomComponent.tsx` :

```typescript
const colorSchemes: Record<string, ColorScheme> = {
  // ... schémas existants
  custom: {
    primary: '#your-color',
    secondary: '#your-secondary-color', 
    background: 'transparent'
  }
}
```

### Positionnement des statistiques

Les statistiques (Min, Max, Mean) sont positionnées automatiquement selon leur valeur dans le range défini :
- **Position angulaire** : `((valeur - min_range) / (max_range - min_range)) * 360°`
- **Texte extérieur** : à `radius + 10px` du centre
- **Indicateur "Mean"** : à `radius - 30px` du centre

## 🛠️ Développement

### Structure du projet

```
st_circular_kpi/
├── st_circular_kpi/
│   ├── __init__.py
│   └── frontend/
│       ├── src/
│       │   ├── CustomComponent.tsx  # Composant React principal
│       │   └── main.tsx
│       ├── package.json
│       └── index.html
├── example.py                       # Exemples d'utilisation
├── setup.py
└── README.md
```

### Lancer l'exemple

```bash
cd st_circular_kpi
python -m streamlit run example.py
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🚀 Versions

### v0.1.0
- ✅ Composant KPI circulaire de base
- ✅ Schémas de couleurs prédéfinis
- ✅ Statistiques visuelles (Min/Max/Mean)
- ✅ Police Urbanist par défaut
- ✅ Arc de fond subtil pour la partie non complétée

---

Créé avec ❤️ par [Antoine](mailto:antoine@example.com)
