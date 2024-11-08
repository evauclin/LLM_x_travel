from model import FormProcessor, extract_parameters
from ticket_master import request_ticket_master





if __name__ == "__main__":
    processor = FormProcessor()
    print("Générateur de paramètres URL initialisé! (Tapez 'quit' pour quitter)")
    print("\nExemples de requêtes:")
    print("- 'Je cherche des concerts à Lyon'")
    print("- 'Événements sportifs à Marseille'")
    print("- 'Spectacles de théâtre à Paris'")

    while True:
        query = input("\nQuelle est votre recherche ? ")
        if query.lower() == 'quit':
            break

        print("\nTruncation was not explicitly activated but `max_length` is provided...")
        print("Setting `pad_token_id` to `eos_token_id`:128001 for open-end generation.\n")

        print("Génération des paramètres...\n")
        response = processor.process_form(query)
        print("Paramètres générés:")
        print(response)

        # Extraire les paramètres
        extracted_params = extract_parameters(response)

        # Créer le dictionnaire de paramètres final
        params = {
            "city": extracted_params["city"],
            "countryCode": extracted_params["countryCode"],
            "locale": "*",
            "classificationName": extracted_params["classificationName"],
            "page": 0
        }

        # Appeler la fonction request_ticket_master
        request_ticket_master(params)