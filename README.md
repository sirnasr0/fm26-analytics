# ⚽ FM26 Scouting Analysis

Analyse de données de scouting sous **Football Manager 26** : extraction, nettoyage et exploration statistique d'un effectif pour identifier les joueurs sous-cotés, les jeunes à potentiel, et comparer les performances par poste.

Projet réalisé pour m'entraîner sur un pipeline complet de data science : **collecte → nettoyage → exploration → visualisation**, sur un jeu de données réel (bien que fictif dans son contenu).

> 🎓 Projet personnel réalisé dans le cadre de ma recherche d'alternance en data science.


## 🎯 Objectifs

- Construire un pipeline de nettoyage robuste à partir de données brutes hétérogènes (texte, formats mixtes, valeurs manquantes)
- Fusionner plusieurs sources de données sur une clé commune
- Explorer les corrélations entre attributs de jeu et performance globale (`Note`)
- Repérer les joueurs sous-cotés (bon niveau / faible salaire) et les jeunes à fort potentiel
- Poser les bases d'un outil de proposition automatique de composition d'équipe (roadmap)

## 🗂 Structure du projet

```
fm26-analytics/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/              ← les 3 CSV bruts (export FM26)
│   └── processed/        ← fm26_data_clean.csv (données nettoyées)
├── notebooks/
│   └── fm26_analyse.ipynb
├── reports/
│   └── figures/          ← visualisations exportées
├── src/
│   └── nettoyage.py       ← fonctions de nettoyage réutilisables et testées
└── tests/
    └── test_nettoyage.py  ← tests unitaires (pytest)
```

## 🛠 Stack technique

- **Python 3.11**
- `pandas` — manipulation et nettoyage de données
- `matplotlib`, `seaborn` — visualisation
- `Jupyter Notebook` — exploration
- `pytest` — tests unitaires sur les fonctions de parsing

## 📊 Aperçu des résultats

| Note vs Salaire | Note moyenne par poste |
|---|---|
| ![note-vs-salaire](reports/figures/note_vs_salaire.png) | ![note-par-poste](reports/figures/note_par_poste.png) |

| Âge vs Note | Corrélation attributs / Note |
|---|---|
| ![age-vs-note](reports/figures/age_vs_note.png) | ![correlation](reports/figures/correlation_attrs.png) |

## 🚀 Installation

```bash
git clone https://github.com/sirnasr0/fm26-analytics.git
cd fm26-analytics
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## 📈 Pipeline de données

1. **Export** — extraction des données FM26 via un plugin dédié (3 fichiers CSV : attributs techniques, mentaux, infos générales)
2. **Fusion** — jointure sur la colonne `Joueur` (34 joueurs)
3. **Nettoyage** — parsing des champs texte hétérogènes :
   - `Matchs disputés` → `Titularisations` / `Remplacements`
   - `Salaire` → valeur numérique normalisée (€/mois)
   - `Montant transfert` → bornes min/max (gestion des fourchettes, "Pas à vendre", unités K/M)
   - `Note` → conversion virgule → point
   - `Expire le` → date, puis calcul des années restantes de contrat
   - `Position` → liste dédoublonnée des postes possibles
4. **Export** → `data/processed/fm26_data_clean.csv` (34 lignes × 40 colonnes)
5. **Exploration** → statistiques descriptives, classements, comparaisons par poste, corrélations

Les fonctions de nettoyage les plus complexes (`convertir_montant`, `extraire_postes`, `extraire_matchs`) sont extraites dans `src/nettoyage.py` et couvertes par des tests unitaires (voir ci-dessous), plutôt que codées en dur dans le notebook.

## 🧪 Tests

Les fonctions de parsing critiques (gestion des fourchettes de prix, formats K/M, extraction des postes multiples) sont testées avec `pytest` :

```bash
pip install -r requirements.txt
pytest
```

## 🗺 Roadmap

- [ ] Récupération des attributs physiques et des données d'entraînement
- [ ] Score composite pour détecter automatiquement les joueurs sous-cotés / jeunes à potentiel
- [ ] Dashboard interactif (Streamlit) pour explorer l'effectif dynamiquement
- [ ] Analyse des performances match par match
- [ ] Proposition automatique de composition d'équipe (11 titulaires + remplaçants) sous contrainte de postes

## 📄 Licence

Ce projet est sous licence MIT — voir [LICENSE](LICENSE).

## 👤 Auteur

ABA-HADDOU Nasr ALLAH — [LinkedIn](https://www.linkedin.com/in/nasr-allah-aba-haddou-234a013a7/) · [GitHub](https://github.com/sirnasr0)
