import asyncio
from scraper import EventbriteScraper
from ticket_master import request_ticket_master

if __name__ == "__main__":
    # Premier scrapping (géré par un collègue)
    params = {
        "city": "Paris",
        "countryCode": "FR",
        "locale": "*",
        "classificationName": "music",
        "page": 0
    }
    # Commentée pour l'instant, mais disponible pour usage
    # request_ticket_master(params)

    # Deuxième scrapping
    EventBrite = EventbriteScraper()

    # Récupération des liens d'événements depuis Eventbrite
    events_links = EventBrite.get_events_links("france", "paris", "soirée")
    events_links = list(set(events_links))
    print("Liens des événements récupérés :", events_links)

    # Construire une chaîne de caractères avec les détails des événements
    events_text = ""

    async def process_links(links):
        global events_text
        for link in links:
            print(f"Traitement de l'événement : {link}")
            try:
                # Récupérer les détails des événements
                event_details = await EventBrite.get_events_infos(link)

                # Ajouter chaque événement au texte avec une mise en forme
                events_text += f"Link: {link}\n"
                for detail in set(event_details):  # Supprimer les doublons éventuels des détails
                    events_text += f"{detail}\n"
                events_text += "\n" + "=" * 40 + "\n\n"  # Séparation entre les événements

            except Exception as e:
                print(f"Erreur lors du traitement de {link}: {e}")

    # Exécuter la récupération des détails avec Playwright
    asyncio.run(process_links(events_links))

    # Écrire les détails des événements dans un fichier texte
    file_name = 'events.txt'
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(events_text)

    print(f"Détails des événements enregistrés dans {file_name}")
