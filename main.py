import json
import asyncio
from event_search import EventSearch

async def main():
    API_KEY = "97ViRGFgMAAjpbWjitt2p3JlLNfoMYQz"
    event_search = EventSearch(API_KEY)

    user_query = input("Veuillez entrer votre requête : ")
    params = event_search.generate_params(user_query)

    if not params:
        print("Impossible de générer les paramètres de recherche.")
        return

    print("Paramètres de recherche:", json.dumps(params, indent=2, ensure_ascii=False))

    events = await event_search.search_events(params)
    event_search.save_events(events)

    with open("output.txt", "r", encoding="utf-8") as file:
        content = file.read()

    custom_user_message = (
        "Voici les informations récupérées : {content}.\n\n"
        "Voici la demande de l'utilisateur : {user_query}\n\n"
        "Je veux que tu respectes le format suivant pour les événements :\n\n"
        "1. Event: Nom de l'événement\n"
        "   Date: Date de l'événement\n"
        "   Lieu: Lieu de l'événement\n"
        "   Description: Extrait de la description de l'événement\n"
        "   Lien Ticketmaster : Lien vers la billetterie\n"
        "   Prix: Prix de l'événement\n\n"
        "il faut top 3 des evenement eventBrite et un top 3 des evenements ticketmaster qui correspondent à la demande de l'utilisateur.\n\n"
        "Il est essentiel de proposer le top 3 des événements qui correspondent à la demande "
        "de l'utilisateur, avec des dates différentes pour chaque événement et dans l'intervalle de dates demandé."
        "Propose des événements à des dates différentes sur la base des informations récupérées."
    )

    response = event_search.generate_response(user_query, content, custom_user_message)
    if response:
        print("\nRecommandations d'événements :")
        print(response)
    else:
        print("Impossible de générer des recommandations.")

    print("\nRecherche terminée. Vérifiez le fichier output.txt pour les résultats.")




if __name__ == "__main__":
    asyncio.run(main())

#je veux faire un voyage a paris afin de d'aller au theatre et sortif entre janvier 2025 et mars 2025