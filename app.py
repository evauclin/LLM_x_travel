import streamlit as st
from PIL import Image
from io import BytesIO
import base64  # Ajouter cette importation

# Fonction pour ajouter à l'historique
def append_history(item):
    if 'history' not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append(item)


# Fonction pour obtenir une réponse via un modèle LLM (à intégrer avec du scraping et LLM pour récupérer les événements)
def get_reply(city, interests):
    # C'est ici que tu intégreras ton scraping ou un LLM pour proposer des événements
    # Pour l'instant, c'est un exemple simple.
    if city and interests:
        return f"Here are some great activities to do in {city} related to {interests}: Event 1, Event 2, Event 3."
    else:
        return "Please provide a city and some interests to get suggestions."

def add_background_image(image_path):
    # Convertir l'image en base64 pour l'utiliser dans le CSS
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")  # Utilisation correcte de base64

    # Ajouter le CSS pour l'image de fond et la couleur des textes
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img_str}");
            background-size: cover;
            background-position: center;
            height: 100vh;
            position: absolute;
            width: 100%;
            top: 0;
            left: 0;
            z-index: -1;
        }}
        /* Changer la couleur du texte global en gris moyen */
        body, .stApp, .css-1d391kg, .css-ffhzg2 {{
            color: #505050; /* Gris moyen */
        }}
        /* Modifier la couleur du texte dans les champs de saisie */
        .stTextInput input, .stTextArea textarea {{
            color: #ffffff;  /* Gris moyen pour les champs de texte */
        }}
        .stTextInput label, .stTextArea label {{
            color: #505050;  /* Gris moyen pour les labels */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Définir l'application Streamlit
def app():
    st.set_page_config(layout="wide")

    add_background_image("trip.png")  # Remplacer par ton chemin d'image

    # Afficher l'introduction
    st.title("Welcome to TravelBot!")
    st.subheader("Get suggestions for activities and events in your chosen city.")

    # Créer un champ de texte pour la ville
    city_input = st.text_input('Where do you want to travel? (City Name)', '')

    # Créer un champ de texte pour les intérêts de l'utilisateur
    interests_input = st.text_area('What kind of activities are you interested in?', '')

    # Afficher l'historique du chat
    if 'history' in st.session_state:
        st.write("Chat History:")
        for item in st.session_state.history:
            st.write(item)

    # Lorsque l'utilisateur soumet sa question
    if st.button('Get Suggestions'):
        append_history(f'User: {city_input} {interests_input}')
        output = get_reply(city_input, interests_input)
        append_history(f'TravelBot: {output}')

        # Afficher l'historique du chat mis à jour
        for item in st.session_state.history:
            st.write(item)

    # Note de bas de page
    st.write(
        "-----------\n\nThis bot uses generative AI to suggest activities and events based on your preferences. "
        "It pulls information from a variety of sources to give you personalized travel ideas!"
    )

    st.write(
        '\n\n\nDisclaimer: The suggestions provided may not be exhaustive or fully accurate depending on available data.'
    )


# Lancer l'application
if __name__ == "__main__":
    app()
