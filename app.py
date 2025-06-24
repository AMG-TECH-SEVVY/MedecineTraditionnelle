import os
import re
import logging
import urllib
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text, Integer, String, SmallInteger, Boolean
import pyodbc
from pandas.api.types import is_numeric_dtype
from sklearn.preprocessing import LabelEncoder
from mlxtend.frequent_patterns import apriori, association_rules

# --- Configuration des logs SQLAlchemy ---
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# --- Constantes globales ---
NOM_SERVEUR = 'DESKTOP-938TJDS\\SQLEXPRESS01'
NOM_BASE = 'AccicentDatabase'
NOM_SCHEMA = 'dbo'
FAMILLES = {
    1: "Identifiants", 2: "Sociodemographiques",
    3: "Contexte", 4: "Explicatives", 9: "Cible"
}
FAM_NAME_TO_CODE = {v: k for k, v in FAMILLES.items()}

# --- Connexion SQL Server ---
def get_engine():
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={NOM_SERVEUR};DATABASE={NOM_BASE};Trusted_Connection=yes;"
    )
    return create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)

engine = get_engine()

# --- Initialisation base + schéma ---
def init_db():
    with pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={NOM_SERVEUR};DATABASE=master;Trusted_Connection=yes;", autocommit=True
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{NOM_BASE}')
            BEGIN CREATE DATABASE [{NOM_BASE}] END
        """)
        cursor.close()
    with engine.begin() as conn:
        conn.execute(text(f"""
            IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{NOM_SCHEMA}')
            EXEC('CREATE SCHEMA {NOM_SCHEMA}')
        """))

init_db()

# --- Fonctions utilitaires ---
def clean_sql_name(name):
    return re.sub(r"[^\w]", "_", os.path.splitext(name)[0]).lower()

def detecter_type(s): 
    return "quantitative" if is_numeric_dtype(s) else "qualitative"

def construire_metadonnees(df):
    return pd.DataFrame({
        "var_id": range(1, len(df.columns) + 1),
        "famv_code": 4,
        "var_code": df.columns,
        "var_libelle": df.columns,
        "var_quanti_quali": [detecter_type(df[c]) for c in df.columns],
        "var_ordre": range(len(df.columns)),
        "var_explicative": 1,
        "var_mesure": 0,
        "var_a_expliquer": 0,
        "Famille": "Explicatives"
    })

def preparer_table(nom_table, df):
    with engine.begin() as conn:
        if conn.dialect.has_table(conn, nom_table, schema=NOM_SCHEMA):
            conn.execute(text(f"TRUNCATE TABLE {NOM_SCHEMA}.{nom_table}"))
        else:
            df.head(0).to_sql(nom_table, engine, schema=NOM_SCHEMA, if_exists="fail", index=False)

def sauvegarder_bdd(meta_df):
    meta_df["famv_code"] = meta_df["Famille"].map(FAM_NAME_TO_CODE)
    meta_df[["var_id", "famv_code", "var_ordre"]] = meta_df[["var_id", "famv_code", "var_ordre"]].astype("int64")
    for col in ["var_explicative", "var_mesure", "var_a_expliquer"]:
        meta_df[col] = meta_df[col].fillna(0).astype("int8")

    dtype_map = {
        "var_id": Integer(), "famv_code": SmallInteger(), "var_code": String(255),
        "var_libelle": String(255), "var_quanti_quali": String(20),
        "var_ordre": SmallInteger(), "var_explicative": Boolean(),
        "var_mesure": Boolean(), "var_a_expliquer": Boolean()
    }

    with engine.begin() as conn:
        conn.execute(text(f"""
        IF NOT EXISTS (
            SELECT * FROM sys.tables 
            WHERE name = 'VARIABLE' AND schema_id = SCHEMA_ID('{NOM_SCHEMA}')
        )
        CREATE TABLE {NOM_SCHEMA}.VARIABLE (
            var_id INT, famv_code SMALLINT, var_code VARCHAR(255),
            var_libelle VARCHAR(255), var_quanti_quali VARCHAR(20),
            var_ordre SMALLINT, var_explicative BIT, var_mesure BIT, var_a_expliquer BIT
        )
        """))
        conn.execute(text(f"TRUNCATE TABLE {NOM_SCHEMA}.VARIABLE"))

    meta_df.drop(columns=["Famille"], errors="ignore").to_sql(
        "VARIABLE", engine, schema=NOM_SCHEMA,
        if_exists="append", index=False, dtype=dtype_map, method="multi"
    )

def preparer_donnees(df, explicatives, cible):
    lbl = LabelEncoder()
    df_enc = df[explicatives + [cible]].apply(lambda s: lbl.fit_transform(s.astype(str)))
    return pd.get_dummies(df_enc.astype(str))

def detecter_regles(df_encoded, cible, min_support=0.01, min_lift=1.0):
    try:
        freq = apriori(df_encoded, min_support=min_support, use_colnames=True, max_len=4)
        if freq.empty: return pd.DataFrame()
        rules = association_rules(freq, metric="lift", min_threshold=min_lift)
        if rules.empty: return pd.DataFrame()
        cible_pat = f"{cible}_"
        rules = rules[rules["consequents"].apply(lambda s: any(cible_pat in str(x) for x in s))]
        return rules[["antecedents", "consequents", "support", "confidence", "lift"]].sort_values("lift", ascending=False)
    except Exception as e:
        st.error(f"Erreur détection règles : {e}")
        return pd.DataFrame()

# --- Interface Streamlit ---
st.set_page_config("OGR - Règles", layout="wide")
st.title("ODR - Outil de Détection de Règles")

uploaded = st.file_uploader("📁 Importer un fichier CSV ou Excel", type=["csv", "xlsx"])

if uploaded:
    if "df_upload" not in st.session_state:
        df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        df.columns = df.columns.str.replace(r"[^\w]", "_", regex=True).str.lower()
        st.session_state["df_upload"] = df
        st.session_state["nom_table"] = clean_sql_name(uploaded.name)
        st.session_state["meta_saved"] = False  # reset flag sauvegarde métadonnées à nouveau fichier uploadé

    df = st.session_state["df_upload"]
    nom_table = st.session_state["nom_table"]

    try:
        preparer_table(nom_table, df)
        chunksize = max(2100 // df.shape[1], 1)
        df.to_sql(nom_table, engine, schema=NOM_SCHEMA, if_exists="append", index=False, method="multi", chunksize=chunksize)
        st.success(f"✅ Données insérées dans {NOM_SCHEMA}.{nom_table}")
    except Exception as e:
        st.error(f"Erreur insertion : {e}")
        st.stop()

    st.header("🧩 Classification des variables")
    meta = construire_metadonnees(df)
    meta_editor = st.data_editor(meta, column_config={
        "Famille": st.column_config.SelectboxColumn("Famille", options=list(FAMILLES.values())),
        "var_explicative": st.column_config.CheckboxColumn("Explicative"),
        "var_a_expliquer": st.column_config.CheckboxColumn("Cible")
    }, disabled=["var_id"], hide_index=True)

    if st.button("💾 Enregistrer les métadonnées"):
        sauvegarder_bdd(meta_editor)
        st.session_state["meta_saved"] = True
        st.success("📌 Table VARIABLE mise à jour.")

    # On affiche la suite uniquement si métadonnées sauvegardées
    if st.session_state.get("meta_saved", False):

        # Recharger les métadonnées depuis la BDD
        meta = pd.read_sql(f"SELECT * FROM {NOM_SCHEMA}.VARIABLE", engine)
        meta["famv_code"] = pd.to_numeric(meta["famv_code"], errors="coerce")
        meta["Famille"] = meta["famv_code"].map(FAMILLES)

        df_data = pd.read_sql(f"SELECT * FROM {NOM_SCHEMA}.{nom_table}", engine)
        cible_vars = meta[meta["Famille"] == "Cible"]["var_code"].tolist()

        if not cible_vars:
            st.warning("⚠️ Aucune variable cible définie.")
        else:
            # --- Détection des règles ---
            st.header("🔍 Détection de règles d'association")
            st.subheader("🎛️ Filtres")

            filtres = {}
            for cat in ["Sociodemographiques", "Contexte"]:
                for col in meta[meta["Famille"] == cat]["var_code"]:
                    options = sorted(df_data[col].dropna().unique().astype(str))
                    choix = st.selectbox(f"{cat} - {col}", ["-- Tout --"] + options, key=f"filtre_{col}")
                    if choix != "-- Tout --":
                        filtres[col] = choix

            cible = st.selectbox("🎯 Variable cible", cible_vars, key="select_cible")
            valeurs = sorted(df_data[cible].dropna().astype(str).unique())
            valeurs_cibles = st.multiselect(f"Valeurs de {cible} à expliquer", valeurs, default=valeurs[:1], key="multiselect_valeurs_cibles")

            if len(valeurs_cibles) == 0:
                st.warning("⚠️ Aucune valeur cible sélectionnée.")
            else:
                expl_vars = st.multiselect("Variables explicatives", meta[meta["Famille"] == "Explicatives"]["var_code"].tolist(), key="multiselect_expl_vars")
                if len(expl_vars) == 0:
                    st.warning("⚠️ Aucune variable explicative sélectionnée.")
                else:
                    # Appliquer filtres
                    df_filtered = df_data.copy()
                    for col, val in filtres.items():
                        df_filtered = df_filtered[df_filtered[col].astype(str) == val]

                    st.info(f"📊 Données après filtrage : {len(df_filtered)} lignes")

                    if len(df_filtered) < 10:
                        st.warning("⚠️ Pas assez de données après filtrage.")
                    else:
                        st.subheader("⚙️ Paramètres Apriori")
                        min_support = 0.01
                        min_lift = 1.0

                        df_target = df_filtered[df_filtered[cible].astype(str).isin(valeurs_cibles)]

                        df_encoded = preparer_donnees(df_target, expl_vars, cible)

                        st.info(f"🧮 Données encodées pour apriori: {df_encoded.shape[0]} lignes, {df_encoded.shape[1]} colonnes")

                        try:
                            freq = apriori(df_encoded, min_support=min_support, use_colnames=True, max_len=4)
                            st.info(f"📈 Itemsets fréquents détectés : {len(freq)}")
                            if freq.empty:
                                st.warning("⚠️ Aucun itemset fréquent trouvé avec ce support.")
                            else:
                                rules = association_rules(freq, metric="lift", min_threshold=min_lift)
                                st.info(f"📊 Règles extraites : {len(rules)}")
                                if rules.empty:
                                    st.warning("⚠️ Aucune règle ne respecte le lift minimum.")
                                else:
                                    cible_pat = f"{cible}_"
                                    rules = rules[rules["consequents"].apply(lambda s: any(cible_pat in str(x) for x in s))]
                                    if rules.empty:
                                        st.warning("⚠️ Aucune règle ne concerne la variable cible sélectionnée.")
                                    else:
                                        rules = rules[["antecedents", "consequents", "support", "confidence", "lift"]].sort_values("lift", ascending=False)
                                        st.success(f"✅ {len(rules)} règle(s) détectée(s)")
                                        st.dataframe(rules)
                        except Exception as e:
                            st.error(f"Erreur lors de la détection des règles : {e}")
