import json
import ollama
import requests
import asyncio
from typing import Dict, List, Optional
import time
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


class OllamaClient:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def chat(self, model: str, messages: List[Dict[str, str]], stream: bool = False) -> Optional[Dict]:
        """Attempt to chat with Ollama with retry logic"""
        for attempt in range(self.max_retries):
            try:
                if stream:
                    response = []
                    stream_response = ollama.chat(
                        model=model,
                        messages=messages,
                        stream=True
                    )
                    for chunk in stream_response:
                        response.append(chunk.get('message', {}).get('content', ''))
                    return {'message': {'content': ''.join(response)}}
                else:
                    return ollama.chat(
                        model=model,
                        messages=messages
                    )
            except KeyboardInterrupt:
                print("\nOpération annulée par l'utilisateur.")
                return None
            except Exception as e:
                if attempt == self.max_retries - 1:
                    print(f"Échec de la communication avec Ollama après {self.max_retries} tentatives: {e}")
                    return None
                print(f"Tentative {attempt + 1} échouée, nouvelle tentative dans {2 ** attempt} secondes...")
                time.sleep(2 ** attempt)


class EventbriteScraper:
    def __init__(self):
        self.base_url = 'https://www.eventbrite.com/d'

    def get_events_links(self, state: str, city: str, category: str) -> List[str]:
        """
        Récupère les liens des événements à partir de la page principale.
        """
        url = f'{self.base_url}/{state}--{city}/{category}'
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            event_elems = soup.find_all(class_='event-card-details')
            events_links = []

            for event_elem in event_elems:
                link_tag = event_elem.find('a', class_='event-card-link')
                if link_tag and 'href' in link_tag.attrs:
                    events_links.append(link_tag['href'])

            return events_links
        except Exception as e:
            print(f"Erreur lors de la récupération des liens Eventbrite: {e}")
            return []

    async def get_events_infos(self, url: str) -> Dict:
        """
        Récupère les détails d'un événement spécifique.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto(url)
                await page.wait_for_timeout(2000)
                event_details = await page.locator('.event-details').all_text_contents()
                await browser.close()
                return event_details
            except Exception as e:
                print(f"Erreur lors de la récupération des détails de l'événement: {e}")
                await browser.close()
                return {}


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


class EventSearch:
    def __init__(self, api_key: str):
        self.ollama_client = OllamaClient()
        self.ticketmaster_client = TicketmasterClient(api_key)
        self.eventbrite_scraper = EventbriteScraper()
        self.system_message = (
            "Tu es un agent de voyage qui génère une liste d'événements "
            "pour aider à planifier un séjour. À partir d'une liste d'événements, "
            "tu dois donner le top 3 des activité et un top 3 des evenements qui correspondent à la demande de l'utilisateur."
        )

    def generate_params(self, user_query: str) -> Optional[Dict]:
        """Generate search parameters from user query"""
        system_message = """
        Analyse cette requête utilisateur pour un événement et retourne uniquement un dictionnaire JSON avec les paramètres suivants :

        {
            "Ticketmaster": {
                "city": "ville mentionnée",
                "countryCode": "code pays (IT pour Italie, FR pour France, ES pour Espagne, etc.)",
                "locale": "*",
                "classificationName": "type d'événement (Music, Sports, Arts, Theatre, etc.)",
                "sort": "date,asc"
            },
            "EventbriteScraper": {
                "state": "état ou région mentionné(e) Exemple: france, italy, spain"
                "city": "ville mentionnée Exemple: paris, rome, madrid"
                "category": "type d'événement ou mot-clé exemple: "theatre" ou "music""
            }
        }
        """

        response = self.ollama_client.chat(
            model='llama3.1:latest',
            messages=[
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': user_query}
            ]
        )

        if not response:
            return None


        content = response['message']['content'].strip()
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        return json.loads(content[json_start:json_end])


    async def search_events(self, params: Dict) -> Dict[str, List[Dict]]:
        """Search events from both Ticketmaster and Eventbrite"""
        ticketmaster_events = self.ticketmaster_client.search_events(
            params.get("Ticketmaster", {})
        )

        eventbrite_params = params.get("EventbriteScraper", {})
        eventbrite_events = []
        if all(key in eventbrite_params for key in ["state", "city", "category"]):
            events_links = self.eventbrite_scraper.get_events_links(
                eventbrite_params["state"],
                eventbrite_params["city"],
                eventbrite_params["category"]
            )
            for link in events_links:
                event_info = {
                    "state": eventbrite_params["state"],
                    "city": eventbrite_params["city"],
                    "category": eventbrite_params["category"],
                    "url": link
                }
                eventbrite_events.append(event_info)

        return {
            "ticketmaster": ticketmaster_events,
            "eventbrite": eventbrite_events
        }

    def save_events(self, events: Dict[str, List[Dict]], filename: str = "output.txt"):
        """Save events to a file"""

        with open(filename, "w", encoding="utf-8") as file:
            # Ticketmaster events
            file.write("=== Événements Ticketmaster ===\n\n")
            if events["ticketmaster"]:
                for event in events["ticketmaster"]:
                    if event:  # Vérifier que l'événement est valide
                        file.write(f"Nom de l'événement: {event['name']}\n")
                        file.write(f"Date: {event['date']}\n")
                        file.write(f"Lieu: {event['venue']}\n")
                        file.write(f"Description: {event['description']}\n")
                        file.write(f"Prix: {event['price']}\n")
                        file.write(f"URL: {event['url']}\n")
                        file.write("-" * 50 + "\n")
                print(f"{len([e for e in events if e])} événements trouvés et enregistrés dans '{filename}'")
            else:
                file.write("Aucun événement trouvé pour ces critères de recherche.\n")
                print("Aucun événement trouvé.")

            # Eventbrite events
            file.write("\n=== Événements Eventbrite ===\n\n")
            if events["eventbrite"]:
                for event in events["eventbrite"]:
                    if event:
                        for key, value in event.items():
                            file.write(f"{key}: {value}\n")
                        file.write("-" * 50 + "\n")
            else:
                file.write("Aucun événement Eventbrite trouvé.\n")

        print(f"Événements enregistrés dans '{filename}'")


    def generate_response(self, user_query: str, content: str, user_message_template: str) -> Optional[str]:
        """Generate a response based on events and user query"""
        formatted_message = user_message_template.format(content=content, user_query=user_query)

        response = self.ollama_client.chat(
            model='llama3.2-vision:latest',
            messages=[
                {'role': 'system', 'content': self.system_message},
                {'role': 'user', 'content': formatted_message}
            ],
            stream=True
        )

        if response:
            return response['message']['content']
        return None


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