import streamlit as st
import requests
from loguru import logger

st.title("🧠 Analyseur de Sentiment")
texte = st.text_area("Entrez votre texte :")

if st.button("Analyser"):
    if texte:
        logger.info(f"Texte à analyser: {texte}")
        try:
            response = requests.post(
                "http://127.0.0.1:9000/analyse_sentiment/",
                json={"texte": texte}
            )
            response.raise_for_status()
            sentiment = response.json()

            st.write(f"Polarité négative : {sentiment['neg']}")
            st.write(f"Polarité neutre : {sentiment['neu']}")
            st.write(f"Polarité positive : {sentiment['pos']}")
            st.write(f"Score composé : {sentiment['compound']}")

            if sentiment['compound'] >= 0.05:
                st.write("Sentiment global : Positif 😀")
            elif sentiment['compound'] <= -0.05:
                st.write("Sentiment global : Négatif 🙁")
            else:
                st.write("Sentiment global : Neutre 😐")
        except Exception as e:
            st.error(f"Erreur : {e}")
            logger.error(f"Erreur : {e}")
    else:
        st.write("Veuillez entrer du texte.")