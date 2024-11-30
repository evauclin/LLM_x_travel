import base64
from PIL import Image
from io import BytesIO
import streamlit as st
import asyncio
from event_search import EventSearch


def add_background_image(image_path):
    img = Image.open(image_path)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

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
        /* Changer la couleur du texte global en noir */
        body, .stApp, .css-1d391kg, .css-ffhzg2 {{
            color: #000000; /* Noir */
        }}
        /* Modifier la couleur du texte dans les champs de saisie en noir */
        .stTextInput input, .stTextArea textarea {{
            color: #000000;  /* Texte en noir */
        }}
        .stTextInput label, .stTextArea label {{
            color: #000000;  /* Labels en noir aussi */
        }}
        /* Changer la couleur de fond des champs de texte */
        .stTextInput input, .stTextArea textarea {{
            background-color: #f0f0f0;  /* Couleur de fond des champs de texte (gris clair) */
        }}
        /* Couleur de fond des champs de texte quand ils sont actifs */
        .stTextInput input:focus, .stTextArea textarea:focus {{
            background-color: #ffffff;  /* Couleur de fond lors de la sélection (blanc) */
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


async def search_events(user_query):
    API_KEY = "97ViRGFgMAAjpbWjitt2p3JlLNfoMYQz"
    event_search = EventSearch(API_KEY)

    params = event_search.generate_params(user_query)

    if not params:
        return "Impossible de générer les paramètres de recherche."

    st.write("### Paramètres de recherche générés :")
    st.json(params)

    events = await event_search.search_events(params)
    event_search.save_events(events)

    with open("output.txt", "r", encoding="utf-8") as file:
        content = file.read()

    custom_user_message = (
        f"Voici les informations récupérées : {content}.\n\n"
        f"Voici la demande de l'utilisateur : {user_query}\n\n"
        "Je veux que tu respectes le format suivant pour les événements :\n\n"
        "1. Event: Nom de l'événement\n"
        "   Date: Date de l'événement\n"
        "   Lieu: Lieu de l'événement\n"
        "   Description: Extrait de la description de l'événement\n"
        "   Lien Ticketmaster : Lien vers la billetterie\n"
        "   Prix: Prix de l'événement\n\n"
        "Il faut top 3 des événements EventBrite et un top 3 des événements Ticketmaster "
        "qui correspondent à la demande de l'utilisateur.\n\n"
        "Il est essentiel de proposer le top 3 des événements qui correspondent à la demande "
        "de l'utilisateur, avec des dates différentes pour chaque événement et dans l'intervalle de dates demandé."
        "Propose des événements à des dates différentes sur la base des informations récupérées."
    )

    response = event_search.generate_response(user_query, content, custom_user_message)
    if response:
        return response
    else:
        return "Impossible de générer des recommandations."


# Fonction principale de l'application
def app():
    st.set_page_config(layout="wide")

    add_background_image("trip.png")

    st.title("Welcome to TravelBot!")
    st.subheader(
        "Tell me what you're looking for, and I'll find events and activities for you!"
    )

    user_query = st.text_area(
        'What is your travel request? (e.g., "I want to travel to Paris for theater and sightseeing between January and March 2025")',
        "",
    )

    if st.button("Get Suggestions"):
        if user_query:
            output = asyncio.run(search_events(user_query))

            st.write("### Suggestions for your request:")
            st.write(output)
        else:
            st.warning("Please enter a valid query!")

    st.write(
        "-----------\n\nThis bot uses generative AI to suggest activities and events based on your preferences. "
        "It pulls information from a variety of sources to give you personalized travel ideas!"
    )

    st.write(
        "\n\n\nDisclaimer: The suggestions provided may not be exhaustive or fully accurate depending on available data."
    )


if __name__ == "__main__":
    app()
