import json
import ollama
import requests
from typing import Dict, List, Optional
import time
from datetime import datetime


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
                events = data.get("_embedded", {}).get("events", [])

                if not events:
                    break

                for event in events:
                    event_info = self._parse_event(event)
                    if event_info:
                        all_events.append(event_info)

                current_page += 1

            except requests.RequestException as e:
                print(f"Erreur lors de la requête Ticketmaster: {e}")
                break
            except KeyboardInterrupt:
                print("\nRecherche interrompue par l'utilisateur.")
                break
            except Exception as e:
                print(f"Erreur inattendue: {e}")
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
        self.system_message = (
            "Tu es un agent de voyage qui génère une liste d'événements "
            "pour aider à planifier un séjour. À partir d'une liste d'événements, "
            "tu dois donner le top 3 qui correspondent à la demande de l'utilisateur."
        )

    def generate_params(self, user_query: str) -> Optional[Dict]:
        """Generate search parameters from user query"""
        system_message = """Analyse cette requête utilisateur pour un événement et retourne uniquement un dictionnaire JSON avec les paramètres suivants, sans texte avant ou après:
        {
            "city": "ville mentionnée",
            "countryCode": "code pays (IT pour Italie, FR pour France, ES pour Espagne, etc.)",
            "locale": "*",
            "classificationName": "type d'événement (Music, Sports, Arts, Theatre, etc.)",
            "sort": "date,asc"
        }

        Si aucun type d'événement n'est spécifié, ne pas inclure classificationName.
        Si aucune ville n'est spécifiée, ne pas inclure city.
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

        try:
            content = response['message']['content'].strip()
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
            raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"Erreur lors du parsing des paramètres: {e}")
            return None

    def generate_response(self, user_query: str, content: str, user_message_template: str) -> Optional[str]:
        """Generate a response based on events and user query"""
        formatted_message = user_message_template.format(content=content, user_query=user_query)

        response = self.ollama_client.chat(
            model='llama3.1:latest',
            messages=[
                {'role': 'system', 'content': self.system_message},
                {'role': 'user', 'content': formatted_message}
            ],
            stream=True
        )

        if response:
            return response['message']['content']
        return None

    def save_events(self, events: List[Dict], filename: str = "output.txt"):
        """Save events to a file"""
        try:
            with open(filename, "w", encoding="utf-8") as file:
                if events:
                    for event in events:
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
        except IOError as e:
            print(f"Erreur lors de l'écriture du fichier: {e}")


def main():
    API_KEY = "97ViRGFgMAAjpbWjitt2p3JlLNfoMYQz"
    event_search = EventSearch(API_KEY)

    try:
        user_query = input("Veuillez entrer votre requête : ")
        params = event_search.generate_params(user_query)

        if not params:
            print("Impossible de générer les paramètres de recherche.")
            return

        print("Paramètres de recherche:", json.dumps(params, indent=2, ensure_ascii=False))
        events = event_search.ticketmaster_client.search_events(params)
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

    except KeyboardInterrupt:
        print("\nProgramme interrompu par l'utilisateur.")
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")


if __name__ == "__main__":
    main()