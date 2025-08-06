import requests
import json
from .config import config
from .helpers import serialize_topics


class InferenceServerService:
    def get_inference_server_url(self):
        return config.get_inference_server_url()

    def set_inference_server_url(self, url):
        config.set_inference_server_url(url)


    def set_inference_server_model(self, model_name, model_type="Transformers", api_key="", inference_type="transformers", attn_implementation="flash_attention_2", move_to_gpu=True, device_map="auto"):
        # """
        # Sets up a model on the inference server.
        # """
        url=config.get_inference_server_url() + "/set_model"
        try:
            response = requests.post(url, json={"model_name": model_name, "model_type": model_type, "api_key": api_key, "inference_type": inference_type, "attn_implementation": attn_implementation, "move_to_gpu": move_to_gpu, "device_map": device_map}, verify=False)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            print(response.json())
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"\nError: Could not connect to the inference server at {url}.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"\nError fetching data from inference server: {e}")
            return None


    def update_topics(self, topics):
        url=config.get_inference_server_url() + "/update_topics"
        try:
            response = requests.post(url, json={"topics": serialize_topics(topics)}, verify=False)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            print(response.json())
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"\nError: Could not connect to the inference server at {url}.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"\nError fetching data from inference server: {e}")
            return None


    




    def get_answer(self, prompt, categories, constrained_output, temperature, thinking_data=None):
        url=config.get_inference_server_url() + "/get_answer"
        try:
            response = requests.post(url, json={"prompt": prompt, "categories": categories, "constrained_output": constrained_output, "temperature": temperature, "thinking_data": thinking_data}, verify=False)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            print(response.json())
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"\nError: Could not connect to the inference server at {url}.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"\nError fetching data from inference server: {e}")
            return None



    def get_non_categorical_answer(self, prompt, topic, constrained_output, temperature, thinking_data=None):
        url=config.get_inference_server_url() + "/get_non_categorical_answer"
        try:
            response = requests.post(url, json={"prompt": prompt, "topic": topic, "constrained_output": constrained_output, "temperature": temperature, "thinking_data": thinking_data}, verify=False)
            print(response.json())
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            answer = response.json().get('answer')
            probability = response.json().get('probability')
            return answer, probability
        except requests.exceptions.ConnectionError:
            print(f"\nError: Could not connect to the inference server at {url}.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"\nError fetching data from inference server: {e}")
            return None



    # def fetch_data_from_server(self):
    #     """
    #     Example function to fetch data from the configured server URL.
    #     """
    #     try:
    #         response = requests.get(f"{self.get_server_url()}/data", verify=False)
    #         response.raise_for_status()  # Raise an exception for bad status codes
    #         return response.json()
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error fetching data from server: {e}")
    #         return None













