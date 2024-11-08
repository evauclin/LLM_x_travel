import requests
from scraper import EventbriteScraper
from ticket_master import request_ticket_master

if __name__ == "__main__":

    # Premier scrapping
    params = {
        "city": "Paris",
        "countryCode": "FR",
        "locale": "*",
        "classificationName": "music",
        "page": 0
    }
    request_ticket_master(params)

    # Deuxième scrapping
    EventBrite = EventbriteScraper()
    events_links = EventBrite.get_events_links("france", "paris", "soirée")

    # Construire une chaîne de caractères avec les détails des événements
    events_text = ""
    for link in events_links:
        print(link)
        event_details = EventBrite.get_events_infos(link)

        # Ajouter chaque événement au texte avec une mise en forme
        events_text += f"Link: {link}\n"
        for key, value in event_details.items():
            events_text += f"{key.capitalize()}: {value}\n"
        events_text += "\n" + "=" * 40 + "\n\n"  # Séparation entre les événements

    # Écrire le texte dans un fichier .txt
    file_name = 'events.txt'
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(events_text)

    EventBrite.quit_driver()
