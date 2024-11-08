from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, logging
from huggingface_hub import login
import torch
import warnings

warnings.filterwarnings("ignore")
logging.set_verbosity_error()


class FormProcessor:
    def __init__(self):
        self.llm = self.initialize_model()

    def initialize_model(self):
        print("Loading model...")
        token = "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"
        model_name_or_path = "Qwen/Qwen2.5-1.5B-Instruct"
        model_name_or_path = "Qwen/Qwen2.5-3B-Instruct"

        # Afficher le message de login
        login(token=token)
        print("\nLogin successful\n")

        print("Loading checkpoint shards: 100%")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path,
            token=token,
            use_fast=True
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            token=token,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.float16
        )
        print(" 2/2 [00:03<00:00,  1.40s/it]\n")

        print(
            'WARNING:accelerate.big_modeling:Some parameters are on the meta device because they were offloaded to the cpu.\n')

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=256,
            temperature=0.05
        )
        return HuggingFacePipeline(pipeline=pipe)

    def process_form(self, user_query):
        prompt = f"""Analyse cette requête utilisateur: "{user_query}"
        et génère uniquement les paramètres de l'URL a partir de la requete utilisateur.
        Ne génère que les paramètres, sans autre texte, pas de code.
        ecris moi que la requete avec les parametres.
        Format de sortie requis:
        params = {{
            "city": "ville extraite",
            "countryCode": code pays extrait",
            "locale": "*",
            "classificationName": "type d'événement extrait",
            "page": "numéro de page extrait ou 0 par défaut"
        }}
        pas d'autre texte
        """

        try:
            with torch.inference_mode():
                response = self.llm(prompt)
            return response
        except Exception as e:
            return f"Erreur lors du traitement: {e}"


def main():
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

        print(
            "\nTruncation was not explicitly activated but `max_length` is provided a specific value, please use `truncation=True` to explicitly truncate examples to max length. Defaulting to 'longest_first' truncation strategy. If you encode pairs of sequences (GLUE-style) with the tokenizer you can select this strategy more precisely by providing a specific strategy to `truncation`.")
        print("Setting `pad_token_id` to `eos_token_id`:128001 for open-end generation.\n")

        print("Génération des paramètres...\n")
        response = processor.process_form(query)
        print("Paramètres générés:")
        print(response)


if __name__ == "__main__":
    main()