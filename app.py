import streamlit as st
import requests
from loguru import logger

# Configuration de Loguru — logs dans le terminal ET dans un fichier
logger.add(
    "logs/app.log",
    rotation="1 MB",
    retention="7 days",
    compression="zip",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

st.set_page_config(
    page_title="FastIA — Analyseur de Sentiment",
    page_icon="🧠",
    layout="centered",
)

st.title("🧠 Analyseur de Sentiment")
st.write("Entrez un texte ci-dessous pour analyser son sentiment grâce au modèle VADER.")
st.divider()


texte = st.text_area(
    label="Votre texte :",
    placeholder="Ex : J'adore ce projet, c'est vraiment passionnant !",
    height=150,
)


if st.button("Analyser", type="primary"):

    if texte:
        logger.info(f"Texte soumis par l'utilisateur : {texte}")

        with st.spinner("Analyse en cours..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:9000/analyse_sentiment/",
                    json={"texte": texte},
                )

                response.raise_for_status()

                sentiment = response.json()
                logger.info(f"Résultats reçus de l'API : {sentiment}")

                st.divider()
                st.subheader("📊 Résultats de l'analyse")

                # scores détaillés dans 3 colonnes
                col1, col2, col3 = st.columns(3)
                col1.metric(label="😠 Négatif", value=sentiment["neg"])
                col2.metric(label="😐 Neutre",  value=sentiment["neu"])
                col3.metric(label="😀 Positif", value=sentiment["pos"])

                st.metric(label="⚖️ Score composé (compound)", value=sentiment["compound"])

                # interprétation globale
                st.divider()
                compound = sentiment["compound"]

                if compound >= 0.05:
                    st.success("Sentiment global : **Positif** 😀")
                    logger.info("Sentiment détecté : Positif")
                elif compound <= -0.05:
                    st.error("Sentiment global : **Négatif** 🙁")
                    logger.info("Sentiment détecté : Négatif")
                else:
                    st.info("Sentiment global : **Neutre** 😐")
                    logger.info("Sentiment détecté : Neutre")

            except requests.exceptions.ConnectionError:
                st.error("❌ Impossible de contacter l'API. Vérifiez que le serveur FastAPI est bien lancé sur le port 9000.")
                logger.error("Erreur de connexion à l'API FastAPI.")

            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Erreur HTTP : {e}")
                logger.error(f"Erreur HTTP : {e}")

            except Exception as e:
                st.error(f"❌ Une erreur est survenue : {e}")
                logger.error(f"Erreur inattendue : {e}")

    else:
        st.warning("⚠️ Veuillez entrer du texte avant de lancer l'analyse.")