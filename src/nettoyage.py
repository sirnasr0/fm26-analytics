"""
Fonctions de nettoyage des données FM26.

Extraites du notebook `nettoyage_fm26.ipynb` pour être testables
et réutilisables indépendamment de l'exploration interactive.
"""

import re


def convertir_montant(texte_montant):
    """
    Convertit un montant de transfert FM26 en tuple (min, max) numérique.

    Gère trois cas de figure :
    - Fourchette : "39M € - 45M €" -> (39 000 000, 45 000 000)
    - Valeur unique : "70M €" -> (70 000 000, 70 000 000)
    - Non-vendable : "Pas à vendre" -> (None, None)

    Args:
        texte_montant (str): la valeur brute issue du CSV FM26.

    Returns:
        tuple[float | None, float | None]: (montant_min, montant_max)
    """
    matches = re.findall(r"([\d,]+)(K|M)", texte_montant)
    valeurs = []
    for nombre, unite in matches:
        nombre = float(nombre.replace(",", "."))
        if unite == "K":
            valeurs.append(nombre * 1_000)
        else:
            valeurs.append(nombre * 1_000_000)

    if len(valeurs) == 0:
        return None, None
    elif len(valeurs) == 1:
        return valeurs[0], valeurs[0]
    else:
        return valeurs[0], valeurs[1]


def convertir_salaire(texte_salaire):
    """
    Convertit un salaire FM26 en valeur numérique mensuelle (€).

    Exemple : "1,6M € p/m" -> 1 600 000.0
              "160K € p/m" -> 160 000.0

    Args:
        texte_salaire (str): la valeur brute issue du CSV FM26.

    Returns:
        float | None: le salaire mensuel en euros, ou None si non trouvé.
    """
    match = re.search(r"([\d,]+)(K|M)", texte_salaire)
    if match is None:
        return None
    nombre, unite = match.groups()
    nombre = float(nombre.replace(",", "."))
    multiplicateur = 1_000 if unite == "K" else 1_000_000
    return nombre * multiplicateur


def extraire_postes(texte_position):
    """
    Extrait la liste dédoublonnée des postes possibles d'un joueur.

    Le format brut mélange plusieurs groupes séparés par des virgules,
    chaque groupe pouvant contenir plusieurs postes séparés par des `/`,
    avec parfois un côté entre parenthèses à ignorer.

    Exemple : "M (C), MO (DGC), BT (C)" -> ["M", "MO", "BT"]

    Args:
        texte_position (str): la valeur brute issue du CSV FM26.

    Returns:
        list[str]: liste dédoublonnée des postes possibles.
    """
    postes = set()
    groupes = texte_position.split(",")
    for groupe in groupes:
        groupe = groupe.strip()
        groupe_sans_cote = re.sub(r"\(.*\)", "", groupe).strip()
        postes_du_groupe = groupe_sans_cote.split("/")
        for poste in postes_du_groupe:
            if poste.strip():
                postes.add(poste.strip())
    return list(postes)


def extraire_matchs(texte_matchs):
    """
    Extrait les titularisations et remplacements depuis le format FM26.

    Exemple : "33 (2)" -> (33, 2)   # 33 titularisations, 2 en tant que remplaçant
              "12"      -> (12, 0)   # aucun remplacement

    Args:
        texte_matchs (str): la valeur brute issue du CSV FM26.

    Returns:
        tuple[int, int]: (titularisations, remplacements)
    """
    titu_match = re.search(r"(\d+)", texte_matchs)
    remp_match = re.search(r"\((\d+)\)", texte_matchs)

    titularisations = int(titu_match.group(1)) if titu_match else 0
    remplacements = int(remp_match.group(1)) if remp_match else 0

    return titularisations, remplacements
