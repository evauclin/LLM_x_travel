import time
from typing import List, Dict, Optional

import ollama


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