import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# =========================================================
# FONCTIONS UTILITAIRES
# =========================================================

def couleur_selon_niveau(valeur):
    """
    Renvoie un code couleur selon le niveau d'un attribut FM26.
    < 10 -> rouge (faible), 10-14 -> orange (moyen), 15+ -> vert (fort)
    """
    if valeur < 10:
        return "#FF4B4B"
    elif valeur < 15:
        return "#FFA500"
    else:
        return "#4CAF50"


# =========================================================
# MÉMOIRE PERSISTANTE (favoris)
# =========================================================
# st.session_state survit entre les réexécutions du script,
# contrairement aux variables normales qui seraient réinitialisées
# à chaque interaction avec l'app.

if "favoris" not in st.session_state:
    st.session_state.favoris = set()


# =========================================================
# CONFIGURATION DE LA PAGE
# =========================================================

st.set_page_config(layout="wide")

# CSS custom pour styliser la navbar (st.radio) en forme de "pilule" arrondie,
# avec la page active surlignée en vert. Streamlit ne permet pas de personnaliser
# ses widgets nativement, donc on cible ici les attributs data-testid internes
# générés par Streamlit pour appliquer notre propre style.
st.markdown("""
<style>
/* Fond arrondi type "pilule" autour des options du radio */
div[data-testid="stRadio"] > div {
    background-color: #1C1F26;
    border-radius: 50px;
    padding: 6px;
    display: inline-flex;
    gap: 4px;
}
/* Chaque option (label) : arrondie, avec transition douce au survol */
div[data-testid="stRadio"] label {
    background-color: transparent;
    border-radius: 40px;
    padding: 8px 20px;
    transition: background-color 0.2s;
    cursor: pointer;
}
div[data-testid="stRadio"] label:hover {
    background-color: #2A2E38;
}
/* Surligne en vert l'option actuellement sélectionnée (:has(input:checked)) */
div[data-testid="stRadio"] label:has(input:checked) {
    background-color: #4CAF50;
}
/* Centre horizontalement le radio à l'intérieur de sa colonne */
div[data-testid="stHorizontalBlock"] div[data-testid="stRadio"] {
    display: flex;
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)

# Navbar centrée : on crée 3 colonnes (1-2-1) et on place le radio uniquement
# dans la colonne du milieu, plus large que les 2 côtés, pour le centrer sur la page.
col_gauche, col_centre, col_droite = st.columns([1, 2, 1])

with col_centre:
    page = st.radio(
        "Navigation",
        ["📊 Général", "✨ Conseils"],
        horizontal=True,
        label_visibility="collapsed"
    )

st.title("FM Scout Analyse")

# =========================================================
# CHARGEMENT DES DONNÉES
# =========================================================

df = pd.read_csv("data/processed/fm26_data_clean.csv")

# Liste de tous les postes uniques présents dans le dataset (utile pour le filtre multiselect).
# On découpe "D/M/AL" en ["D", "M", "AL"], on éclate chaque liste en lignes séparées (explode),
# puis on ne garde que les valeurs uniques, triées par ordre alphabétique.

postes_uniques = sorted(df["Postes possibles"].str.split("/").explode().unique())

# Regroupement des colonnes par catégorie, utilisé plus bas pour le filtre d'affichage du tableau.

colonnes_technique = ["Corners", "Centres", "Finition", "Contrôle de balle", "Coups francs",
                      "Jeu de tête", "Tirs de loin", "Touches longues", "Passes", "Penalty",
                      "Tacles", "Technique"]

colonnes_mental = ["Agressivité", "Anticipation", "Courage", "Sang-froid", "Concentration",
                    "Décisions", "Appels de balle", "Placement", "Travail d'équipe",
                    "Vision du jeu", "Volume de jeu"]

colonnes_general = ["Âge", "Note", "Buts", "Passes décisives", "Salaire (€/mois)",
                    "Postes possibles", "Titularisations", "Remplacements"]

if page == "📊 Général":
    # =========================================================
    # SIDEBAR — FILTRES
    # =========================================================

    st.sidebar.header("Filtres")

    # Recherche par nom (texte libre, insensible à la casse, appliquée plus bas)

    recherche_nom = st.sidebar.text_input("🔍 Rechercher un joueur")

    # Filtre par tranche d'âge

    age_min = int(df["Âge"].min())
    age_max = int(df["Âge"].max())
    age_selectionne = st.sidebar.slider("Âge", age_min, age_max, (age_min, age_max))

    # Filtre par poste (un joueur peut avoir plusieurs postes possibles)

    postes_selectionne = st.sidebar.multiselect(
        "Postes",
        postes_uniques,
        default=postes_uniques
    )


    def a_un_poste_selectionne(postes_du_joueur):
        """
        Renvoie True si AU MOINS UN des postes du joueur fait partie
        des postes actuellement sélectionnés dans le filtre.
        """
        liste_postes_joueur = postes_du_joueur.split("/")
        return any(poste in postes_selectionne for poste in liste_postes_joueur)


    # Application des filtres âge + poste sur le DataFrame principal

    df_filtre = df[
        (df["Âge"].between(age_selectionne[0], age_selectionne[1]))
        & (df["Postes possibles"].apply(a_un_poste_selectionne))
    ]

    # Application du filtre de recherche par nom (si l'utilisateur a tapé quelque chose)

    if recherche_nom:
        df_filtre = df_filtre[df_filtre["Joueur"].str.contains(recherche_nom, case=False, na=False)]


    # --- Filtre : quelles catégories de colonnes afficher dans le tableau ---

    st.sidebar.header("Colonnes à afficher")

    afficher_technique = st.sidebar.checkbox("Attributs techniques", value=True)
    afficher_mental = st.sidebar.checkbox("Attributs mentaux", value=True)
    afficher_general = st.sidebar.checkbox("Infos générales", value=True)

    # On construit la liste des colonnes à afficher selon les cases cochées.
    # "Joueur" est toujours affiché en premier.

    colonnes_a_afficher = ["Joueur"]

    if afficher_technique:
        colonnes_a_afficher += colonnes_technique
    if afficher_mental:
        colonnes_a_afficher += colonnes_mental
    if afficher_general:
        colonnes_a_afficher += colonnes_general


    # --- Filtre : n'afficher que les joueurs marqués en favoris ---

    st.sidebar.header("⭐ Favoris")
    afficher_favoris_uniquement = st.sidebar.checkbox("⭐ Afficher seulement les favoris")

    if afficher_favoris_uniquement:
        df_filtre = df_filtre[df_filtre["Joueur"].isin(st.session_state.favoris)]


    # =========================================================
    # KPIs — indicateurs résumés en haut de page
    # =========================================================

    col1, col2, col3 = st.columns(3)

    col1.metric("Nombre de joueurs", len(df_filtre))
    col2.metric("Note moyenne", round(df_filtre["Note"].mean(), 2))
    col3.metric("Âge moyen", round(df_filtre["Âge"].mean(), 1))


    # =========================================================
    # TABLEAU DE L'EFFECTIF + SYSTÈME DE FAVORIS
    # =========================================================

    def mettre_a_jour_favoris():
        """
        Callback déclenché immédiatement quand une case '⭐ Favori' est cochée/décochée
        dans le tableau (st.data_editor). On lit les lignes modifiées via
        st.session_state, puis on met à jour l'ensemble des favoris en mémoire.
        Utiliser un callback évite le bug de décalage d'un clic qu'on aurait
        en relisant simplement le résultat après affichage.
        """
        edits = st.session_state["editeur_favoris"]["edited_rows"]
        for index_ligne, modification in edits.items():
            nom_joueur = df_avec_favoris.iloc[index_ligne]["Joueur"]
            if modification.get("⭐ Favori") is True:
                st.session_state.favoris.add(nom_joueur)
            elif modification.get("⭐ Favori") is False:
                st.session_state.favoris.discard(nom_joueur)


    # Construction du tableau affiché : colonnes sélectionnées + colonne favori en 1ère position

    df_avec_favoris = df_filtre[colonnes_a_afficher].copy()
    df_avec_favoris.insert(0, "⭐ Favori", df_avec_favoris["Joueur"].isin(st.session_state.favoris))

    # st.data_editor (au lieu de st.dataframe) permet d'avoir une colonne cliquable/éditable.
    # Seule la colonne "⭐ Favori" est modifiable (disabled=colonnes_a_afficher verrouille le reste).

    st.data_editor(
        df_avec_favoris,
        use_container_width=True,
        disabled=colonnes_a_afficher,
        hide_index=True,
        key="editeur_favoris",
        on_change=mettre_a_jour_favoris
    )

    # Export CSV de la sélection actuellement affichée

    csv_a_telecharger = df_avec_favoris.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Télécharger cette sélection en CSV",
        data=csv_a_telecharger,
        file_name="fm26_selection.csv",
        mime="text/csv"
    )


    # =========================================================
    # PRÉPARATION DES DONNÉES POUR LES GRAPHIQUES
    # =========================================================

    # Note moyenne par poste : on éclate "Postes possibles" pour qu'un joueur
    # multi-postes compte dans chacun de ses postes (pas comme un groupe à part).

    df_explose = df_filtre.copy()
    df_explose["Poste"] = df_explose["Postes possibles"].str.split("/")
    df_explose = df_explose.explode("Poste")

    note_par_poste = df_explose.groupby("Poste")["Note"].mean().sort_values(ascending=False).reset_index()

    # Contribution offensive (buts + passes décisives) et poste principal (1er poste de la liste)

    df_contrib = df_filtre.copy()
    df_contrib["Contribution offesive"] = df_contrib["Buts"] + df_contrib["Passes décisives"]
    df_contrib["Poste principal"] = df_contrib["Postes possibles"].str.split("/").str[0]

    # Corrélation de chaque attribut avec la Note globale

    attrs = ["Corners", "Centres", "Finition", "Contrôle de balle", "Coups francs",
            "Jeu de tête", "Tirs de loin", "Touches longues", "Passes", "Penalty",
            "Tacles", "Technique", "Agressivité", "Anticipation", "Courage",
            "Sang-froid", "Concentration", "Décisions", "Appels de balle",
            "Placement", "Travail d'équipe", "Vision du jeu", "Volume de jeu", "Note"]

    corr = df_filtre[attrs].corr()[["Note"]].drop("Note").sort_values("Note", ascending=False).reset_index()
    corr.columns = ["Attribut", "Corrélation"]


    # =========================================================
    # GRAPHIQUES — ligne 1 : Note vs Salaire / Note par poste
    # =========================================================

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Note vs Salaire")
        fig = px.scatter(
            df_filtre,
            x="Salaire (€/mois)",
            y="Note",
            hover_name="Joueur",
            log_x=True,
            height=500
        )

        # Graduations personnalisées sur l'axe logarithmique du salaire (plus lisible
        # que les sous-graduations automatiques 2,3,4,5... de Plotly)

        fig.update_xaxes(
            rangeslider_visible=False,
            tickvals=[100_000, 200_000, 300_000, 500_000, 750_000, 1_000_000, 1_500_000, 2_000_000],
            ticktext=["100k", "200k", "300k", "500k", "750k", "1M", "1.5M", "2M"]
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Note moyenne par poste")

        fig2 = px.bar(
            note_par_poste,
            x="Poste",
            y="Note",
            height=500
        )

        # Échelle Y resserrée (4 à note_max+0.5) pour mieux voir les écarts entre postes
        fig2.update_yaxes(range=[4, note_par_poste["Note"].max() + 0.5], dtick=0.5)
        st.plotly_chart(fig2, use_container_width=True)


    # =========================================================
    # GRAPHIQUES — ligne 2 : Âge vs Note / Corrélations
    # =========================================================

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Âge vs Note")

        fig3 = px.scatter(
            df_contrib,
            x="Âge",
            y="Note",
            size="Contribution offesive",   # taille du point = contribution offensive
            color="Poste principal",         # couleur = poste principal du joueur
            hover_name="Joueur",
            height=500
        )

        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        st.subheader("Corrélation attributs / Note")

        fig4 = px.bar(
            corr,
            x="Corrélation",
            y="Attribut",
            orientation="h",  # barres horizontales, plus lisibles avec beaucoup de catégories
            height=700
        )

        st.plotly_chart(fig4, use_container_width=True)


    # =========================================================
    # FICHE JOUEUR — vue détaillée d'un joueur sélectionné
    # =========================================================

    st.divider()
    st.subheader("🔍 Fiche Joueur")

    # Sélecteur : liste des joueurs actuellement filtrés, triée par ordre alphabétique

    joueur_selectionne = st.selectbox(
        "Choisir un joueur",
        df_filtre["Joueur"].sort_values()
    )

    # Récupération de la ligne complète du joueur choisi

    donnees_joueur = df_filtre[df_filtre["Joueur"] == joueur_selectionne].iloc[0]

    # --- Métriques rapides (poste, âge, note, salaire) ---

    col_x, col_y, col_z, col_w = st.columns(4)

    col_x.metric("Poste(s)", donnees_joueur["Postes possibles"])
    col_y.metric("Âge", int(donnees_joueur["Âge"]))
    col_z.metric("Note", donnees_joueur["Note"])
    col_w.metric("Salaire (€/mois)", f"{donnees_joueur['Salaire (€/mois)']:,.0f} €".replace(",", " "))

    # Sous-ensemble d'attributs choisis pour le radar (8 attributs variés, lisible sur le graphique)

    attributs_radar = ["Finition", "Passes", "Technique", "Tacles", "Vision du jeu",
                        "Sang-froid", "Anticipation", "Placement"]

    valeurs_radar = donnees_joueur[attributs_radar].tolist()

    # --- Mise en page : radar chart à gauche, infos détaillées à droite ---

    col_radar, col_stats = st.columns([1, 1.2])

    with col_radar:
        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(
            r=valeurs_radar,
            theta=attributs_radar,
            fill='toself',
            name=joueur_selectionne
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 20], showticklabels=False),  # cache les 0/5/10/15/20
                bgcolor="rgba(0,0,0,0)"  # fond transparent à l'intérieur du radar
            ),
            paper_bgcolor="rgba(0,0,0,0)",  # fond transparent autour du graphique
            height=500
        )

        st.plotly_chart(fig_radar, use_container_width=True)

    with col_stats:
        
        # Infos contractuelles en gros format (metric), sur 2 colonnes

        sous_col_1, sous_col_2 = st.columns(2)

        sous_col_1.metric("Contrat jusqu'au", str(donnees_joueur["Expire le"])[:10])
        sous_col_2.metric("Années restantes", f"{donnees_joueur['Années restantes contrat']:.1f} ans")

        sous_col_1.metric("Titularisations", int(donnees_joueur["Titularisations"]))
        sous_col_2.metric("Remplacements", int(donnees_joueur["Remplacements"]))

        st.markdown("**Attributs clés**")

        # Attributs affichés sur 2 colonnes, colorés selon leur niveau (rouge/orange/vert)
        
        sous_col_3, sous_col_4 = st.columns(2)
        colonnes_attributs = [sous_col_3, sous_col_4]

        for i, attribut in enumerate(attributs_radar):
            valeur = donnees_joueur[attribut]
            couleur = couleur_selon_niveau(valeur)
            colonne_cible = colonnes_attributs[i % 2]  # alterne entre les 2 colonnes
            colonne_cible.markdown(
                f"{attribut} : <span style='color:{couleur}; font-weight:bold'>{valeur}</span>",
                unsafe_allow_html=True
            )

elif page == "✨ Conseils":

    # =========================================================
    # PAGE CONSEILS — score composite et recommandations
    # =========================================================
    # Le score est calculé sur TOUT le dataset (df, pas df_filtre), pour que
    # les moyennes et écarts-types utilisés dans les z-scores restent
    # statistiquement fiables, indépendamment des filtres de la page Général.

    st.subheader("💡 Joueurs sous-côtés et joueurs à vendre")

    # Standardisation de chaque critère en z-score : (valeur - moyenne) / écart-type.
    # Un z-score de +1 signifie "1 écart-type au-dessus de la moyenne du dataset".
    # Ça permet de comparer des critères aux échelles très différentes (une Note
    # sur 20 et un Salaire en centaines de milliers d'euros) sur une base commune.

    z_note = (df["Note"] - df["Note"].mean()) / df["Note"].std()
    z_salaire = (df["Salaire (€/mois)"] - df["Salaire (€/mois)"].mean()) / df["Salaire (€/mois)"].std()
    z_age = (df["Âge"] - df["Âge"].mean()) / df["Âge"].std()

    # Score "sous-coté" : élevé si bonne note, salaire bas et joueur jeune
    # (d'où les signes négatifs devant z_salaire et z_age).

    df["Score sous-cote"] = z_note - z_salaire - z_age

    # Score "à vendre" : la logique inverse — élevé si salaire élevé,
    # note faible et joueur âgé.

    df["Score a vendre"] = z_salaire - z_note + z_age

    col_sous_cote, col_a_vendre = st.columns(2)

    with col_sous_cote:
        st.markdown("### 🟢 TOP 10 des joueurs les plus sous-côtés :")

        # Tri par score décroissant, on ne garde que les 10 meilleurs

        top_sous_cote = df.sort_values("Score sous-cote", ascending=False).head(10)
        colonnes_affichees = ["Joueur", "Âge", "Note", "Salaire (€/mois)", "Postes possibles", "Score sous-cote"]

        # .style.background_gradient() applique un dégradé de couleur en fond de
        # cellule selon la valeur (ici uniquement sur la colonne du score),
        # pour repérer visuellement les meilleurs candidats en un coup d'œil.

        st.dataframe(
            top_sous_cote[colonnes_affichees].style.background_gradient(
                subset=["Score sous-cote"], cmap="RdYlGn"
            ),
            use_container_width=True,
            hide_index=True
        )

    with col_a_vendre:
        st.markdown("### 🔴 TOP 10 des joueurs à vendre :")
        top_a_vendre = df.sort_values("Score a vendre", ascending=False).head(10)
        colonnes_affichees_vente = ["Joueur", "Âge", "Note", "Salaire (€/mois)", "Postes possibles", "Score a vendre"]
        st.dataframe(
            top_a_vendre[colonnes_affichees_vente].style.background_gradient(
                subset=["Score a vendre"], cmap="RdYlGn"
            ),
            use_container_width=True,
            hide_index=True
        )