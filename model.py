from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, logging
from huggingface_hub import login
import torch
import warnings
import re

from ticket_master import request_ticket_master

warnings.filterwarnings("ignore")
logging.set_verbosity_error()


def extract_parameters(response_text):
    # Trouver tous les blocs de paramètres dans le texte
    params_matches = list(re.finditer(r'params\s*=\s*{([^}]+)}', response_text))

    # Prendre le dernier bloc de paramètres (celui avec les vraies valeurs)
    if len(params_matches) > 0:
        param_text = params_matches[-1].group(1)

        # Extraire les valeurs
        city_match = re.search(r'"city":\s*"([^"]+)"', param_text)
        country_match = re.search(r'"countryCode":\s*"([^"]+)"', param_text)
        class_match = re.search(r'"classificationName":\s*"([^"]+)"', param_text)
        page_match = re.search(r'"page":\s*"([^"]+)"', param_text)

        return {
            "city": city_match.group(1) if city_match else "",
            "countryCode": country_match.group(1) if country_match else "",
            "locale": "*",
            "classificationName": class_match.group(1) if class_match else "",
            "page": "0"
        }
    else:
        return {
            "city": "",
            "countryCode": "",
            "locale": "*",
            "classificationName": "",
            "page": "0"
        }


class FormProcessor:
    def __init__(self):
        self.llm = self.initialize_model()

    def initialize_model(self):
        print("Loading model...")
        token = "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"
        model_name_or_path = "Qwen/Qwen2.5-1.5B-Instruct"

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
            "countryCode": "code pays extrait",
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

