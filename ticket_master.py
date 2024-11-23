from typing import Dict, List, Optional

import requests


class TicketmasterClient:
    def __init__(self, api_key: str, max_pages: int = 5):
        self.api_key = api_key
        self.max_pages = max_pages
        self.base_url = "https://app.ticketmaster.com/discovery/v2/events.json"

    def search_events(self, params: Dict) -> List[Dict]:
        """Search for events with pagination and error handling"""
        all_events = []
        current_page = 0

        while current_page < self.max_pages:
            try:
                search_params = {
                    **params,
                    "apikey": self.api_key,
                    "page": str(current_page),
                    "size": "20"
                }

                response = requests.get(
                    self.base_url,
                    params=search_params,
                    timeout=30
                )
                response.raise_for_status()

                data = response.json()
                page_events = data.get("_embedded", {}).get("events", [])

                if not page_events:
                    break

                for event in page_events:
                    event_info = self._parse_event(event)
                    if event_info:
                        all_events.append(event_info)

                current_page += 1

            except Exception as e:
                print(f"Erreur lors de la requête Ticketmaster: {e}")
                break

        return all_events

    def _parse_event(self, event: Dict) -> Optional[Dict]:
        """Parse a single event into a structured format"""
        try:
            event_info = {
                "name": event['name'],
                "date": event['dates']['start']['localDate'],
                "venue": event['_embedded']['venues'][0]['name'],
                "description": event.get('description', "Aucune description disponible"),
                "price": "Informations non disponibles",
                "url": event.get('url', "Lien non disponible")
            }

            if price_ranges := event.get("priceRanges"):
                min_price = price_ranges[0].get("min")
                max_price = price_ranges[0].get("max")
                currency = price_ranges[0].get("currency", "EUR")
                event_info["price"] = f"de {min_price} à {max_price} {currency}"

            return event_info
        except KeyError as e:
            print(f"Erreur lors du parsing d'un événement: {e}")
            return None
