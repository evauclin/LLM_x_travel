import requests

def request_ticket_master(params) -> str:
    """
    Found all events from TicketMaster API
    :param params:
    :return:
    """
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params["apikey"] = "97ViRGFgMAAjpbWjitt2p3JlLNfoMYQz"

    all_events = []
    while True:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Erreur lors de la récupération des données :", response.status_code)
            break

        data = response.json()
        events = data.get("_embedded", {}).get("events", [])

        if not events:
            print("Toutes les pages ont été récupérées.")
            break

        for event in events:
            event_info = {
                "name": event['name'],
                "date": event['dates']['start']['localDate'],
                "venue": event['_embedded']['venues'][0]['name'],
                "description": event.get('description', "Aucune description disponible"),
                "url": event.get("url", "Lien non disponible")  # Ajout du lien de l'événement
            }

            price_ranges = event.get("priceRanges")
            if price_ranges:
                min_price = price_ranges[0].get("min")
                max_price = price_ranges[0].get("max")
                currency = price_ranges[0].get("currency", "EUR")
                event_info["price"] = f"de {min_price} à {max_price} {currency}"
            else:
                event_info["price"] = "Informations non disponibles"

            all_events.append(event_info)

        params["page"] += 1

    with open("output.txt", "w", encoding="utf-8") as file:
        for event in all_events:
            file.write(f"Nom de l'événement: {event['name']}\n")
            file.write(f"Date: {event['date']}\n")
            file.write(f"Lieu: {event['venue']}\n")
            file.write(f"Description: {event['description']}\n")
            file.write(f"Prix: {event['price']}\n")
            file.write(f"Lien Ticketmaster: {event['url']}\n")  # Ajout du lien dans le fichier
            file.write("-" * 20 + "\n")

    print("Les informations des événements ont été enregistrées dans 'output.txt'.")
