"""
Tests unitaires pour les fonctions de nettoyage FM26.

Lancer avec : pytest
"""

import sys
from pathlib import Path

# Permet d'importer src/ sans installer le package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.nettoyage import (
    convertir_montant,
    convertir_salaire,
    extraire_postes,
    extraire_matchs,
)


# --- convertir_montant ---

def test_montant_fourchette():
    assert convertir_montant("39M € - 45M €") == (39_000_000, 45_000_000)


def test_montant_valeur_unique():
    assert convertir_montant("70M €") == (70_000_000, 70_000_000)


def test_montant_pas_a_vendre():
    assert convertir_montant("Pas à vendre") == (None, None)


def test_montant_unites_mixtes():
    assert convertir_montant("100K € - 250K €") == (100_000, 250_000)


def test_montant_virgule_decimale():
    assert convertir_montant("1,5M € - 2M €") == (1_500_000, 2_000_000)


# --- convertir_salaire ---

def test_salaire_millions():
    assert convertir_salaire("1,6M € p/m") == 1_600_000.0


def test_salaire_milliers():
    assert convertir_salaire("160K € p/m") == 160_000.0


def test_salaire_format_invalide():
    assert convertir_salaire("Non disponible") is None


# --- extraire_postes ---

def test_postes_simple():
    assert extraire_postes("D (C)") == ["D"]


def test_postes_slash():
    assert set(extraire_postes("D/AL/M (D)")) == {"D", "AL", "M"}


def test_postes_groupes_multiples():
    resultat = extraire_postes("M (C), MO (DGC), BT (C)")
    assert set(resultat) == {"M", "MO", "BT"}


def test_postes_dedoublonnage():
    # "D" apparaît dans deux groupes différents, ne doit apparaître qu'une fois
    resultat = extraire_postes("D/AL (G), MD, M/MO (G)")
    assert sorted(resultat) == sorted(["M", "AL", "D", "MD", "MO"])
    assert len(resultat) == len(set(resultat))  # pas de doublons


def test_postes_sans_parentheses():
    assert extraire_postes("MD, M/MO (C)") == extraire_postes("MD, M/MO (C)")
    assert set(extraire_postes("MD, M/MO (C)")) == {"MD", "MO", "M"}


# --- extraire_matchs ---

def test_matchs_avec_remplacements():
    assert extraire_matchs("33 (2)") == (33, 2)


def test_matchs_sans_remplacements():
    assert extraire_matchs("12") == (12, 0)


def test_matchs_zero():
    assert extraire_matchs("0") == (0, 0)
