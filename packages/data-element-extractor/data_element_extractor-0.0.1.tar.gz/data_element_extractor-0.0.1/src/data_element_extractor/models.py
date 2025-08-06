import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteria
from openai import OpenAI
from .inference_server_service import InferenceServerService
from .model_answers import ModelAnswersManager
from .prompt_optimizer import prompt_optimizer_generate_improved_prompt, prompt_optimizer_create_thinking_prompt


class ModelManager:
    def __init__(self):
        
        # Attributes for the main model
        self.model_name = ""
        self.model_type = ""
        self.inference_type = ""
        self.tokenizer = None
        self.llm = None
        self.client = None
        self.max_seq_length = None # To store model's max sequence length
        self.api_key = ""
        self.attn_implementation = "flash_attention_2"
        self.move_to_gpu = True
        self.device_map = "auto"


        # Attributes for the prompt generation/improvement model
        self.prompt_model_name = ""
        self.prompt_model_type = ""
        self.prompt_inference_type = ""
        self.prompt_tokenizer = None
        self.prompt_llm = None
        self.prompt_client = None
        self.prompt_max_seq_length = None
        self.prompt_api_key = "" # To store API key for the prompt model
        self.prompt_attn_implementation = "flash_attention_2"
        self.prompt_move_to_gpu = True
        self.prompt_device_map = "auto"

        # Model answers manager
        self.model_answers_manager = ModelAnswersManager()
        # Inference server attributes
        self.inference_server_service = InferenceServerService()



    def set_model(self, model_name, model_type="Transformers", api_key="", inference_type="transformers", attn_implementation="flash_attention_2", move_to_gpu=True, device_map="auto"):
        self.model_name = model_name
        self.model_type = model_type
        self.inference_type = inference_type
        self.attn_implementation = attn_implementation
        self.move_to_gpu = move_to_gpu


        if inference_type == "server":
            self.inference_type = "server"
            self.set_inference_server_model(model_name=model_name, model_type=model_type, api_key=api_key, inference_type=inference_type, attn_implementation=attn_implementation, move_to_gpu=move_to_gpu, device_map=device_map)

        else:
            if self.model_type == "Transformers":
                if self.inference_type == "transformers":
                    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
                    self.llm = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        trust_remote_code=True,
                        torch_dtype=dtype,
                        attn_implementation=attn_implementation,
                        device_map=device_map,
                    )
                    
                    if move_to_gpu:
                        self.llm.to(self.llm.device)
                        print(f"Model moved to {self.llm.device}")
                    self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
                    # Determine and store max sequence length
                    if hasattr(self.tokenizer, 'model_max_length') and self.tokenizer.model_max_length:
                        self.max_seq_length = self.tokenizer.model_max_length
                    elif hasattr(self.llm, 'config') and hasattr(self.llm.config, 'max_position_embeddings') and self.llm.config.max_position_embeddings:
                        self.max_seq_length = self.llm.config.max_position_embeddings
                    else:
                        self.max_seq_length = 512 # Default fallback, though specific model max length is preferred
                        print(f"Warning: Could not automatically determine max sequence length for {self.model_name}. Defaulting to {self.max_seq_length}. This might cause issues.")
                else:
                    print("Invalid inference Type for Transformers.")
            elif self.model_type == "OpenAI":
                self.inference_type = "cloud"
                if api_key:
                    self.client = OpenAI(api_key=api_key)
            elif self.model_type == "DeepInfra":
                self.inference_type = "cloud"
                if api_key:
                    self.client = OpenAI(api_key=api_key, base_url="https://api.deepinfra.com/v1/openai")



    def set_model_as_prompt_model(self):
        self.prompt_model_name = self.model_name
        self.prompt_model_type = self.model_type
        self.prompt_inference_type = self.inference_type
        self.prompt_api_key = self.api_key
        self.prompt_attn_implementation = self.attn_implementation
        self.prompt_move_to_gpu = self.move_to_gpu
        self.prompt_device_map = self.device_map
        self.prompt_tokenizer = self.tokenizer
        self.prompt_llm = self.llm

    def set_prompt_model(self, model_name, model_type="OpenAI", api_key="", inference_type="cloud", attn_implementation="flash_attention_2", move_to_gpu=True, device_map="auto"):
        self.prompt_model_name = model_name
        self.prompt_model_type = model_type
        self.prompt_inference_type = inference_type
        self.prompt_api_key = api_key # Store the API key
        self.prompt_attn_implementation = attn_implementation
        self.prompt_move_to_gpu = move_to_gpu
        self.prompt_device_map = device_map

        if self.prompt_model_type == "Transformers":
            # For local prompt generation, we'll assume 'transformers' inference type for now
            # The 'guidance' type would require more specific setup as seen in previous_code.py
            self.prompt_inference_type = "transformers" # Override if set differently for local model
            try:
                dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
                self.prompt_tokenizer = AutoTokenizer.from_pretrained(self.prompt_model_name, trust_remote_code=True)
                self.prompt_llm = AutoModelForCausalLM.from_pretrained(
                    self.prompt_model_name,
                    trust_remote_code=True,
                    torch_dtype=dtype,
                    device_map=device_map,
                    attn_implementation = attn_implementation,  
                )
                if move_to_gpu:
                    self.prompt_llm.to('cuda')
                self.prompt_tokenizer.pad_token_id = self.prompt_tokenizer.eos_token_id
                if hasattr(self.prompt_tokenizer, 'model_max_length') and self.prompt_tokenizer.model_max_length:
                    self.prompt_max_seq_length = self.prompt_tokenizer.model_max_length
                elif hasattr(self.prompt_llm, 'config') and hasattr(self.prompt_llm.config, 'max_position_embeddings') and self.prompt_llm.config.max_position_embeddings:
                    self.prompt_max_seq_length = self.prompt_llm.config.max_position_embeddings
                else:
                    self.prompt_max_seq_length = 512 # Default fallback
                    print(f"Warning: Could not automatically determine max sequence length for prompt_model {self.prompt_model_name}. Defaulting to {self.prompt_max_seq_length}.")
            except Exception as e:
                print(f"Error setting up local prompt_model ({self.prompt_model_name}): {e}")
                self.prompt_llm = None # Ensure it's None if setup fails

        elif self.prompt_model_type == "OpenAI":
            self.prompt_inference_type = "cloud"
            if api_key:
                self.prompt_client = OpenAI(api_key=api_key)
            else:
                print("API key required for OpenAI prompt_model.")
        elif self.prompt_model_type == "DeepInfra":
            self.prompt_inference_type = "cloud"
            if api_key:
                self.prompt_client = OpenAI(api_key=api_key, base_url="https://api.deepinfra.com/v1/openai")
            else:
                print("API key required for DeepInfra prompt_model.")
        else:
            print(f"Unsupported prompt_model_type: {self.prompt_model_type}")





    ### Answer Models        


    def set_inference_server_model(self, model_name, model_type="Transformers", api_key="", inference_type="transformers", attn_implementation="flash_attention_2", move_to_gpu=True, device_map="auto"):
        self.inference_server_service.set_inference_server_model(model_name=model_name, model_type=model_type, api_key=api_key, inference_type=inference_type, attn_implementation=attn_implementation, move_to_gpu=move_to_gpu, device_map=device_map)



    def extract_element(self, topic, text, constrained_output=False, thinking_data=None):
        return self.model_answers_manager.extract_element(
            topic=topic, 
            text=text, 
            constrained_output=constrained_output, 
            inference_type=self.inference_type,
            thinking_data=thinking_data,
            tokenizer=self.tokenizer,
            llm=self.llm,
            max_seq_length=self.max_seq_length
            )
                

    def get_answer(self, prompt, categories, constrained_output, temperature=0.0, thinking_data=None):
        return self.model_answers_manager.get_answer(prompt, categories, constrained_output, temperature, thinking_data, inference_type=self.inference_type, client=self.client, model_name=self.model_name, tokenizer=self.tokenizer, llm=self.llm, max_seq_length=self.max_seq_length)


    def get_non_categorical_answer(self, prompt, topic, constrained_output, temperature=0.0, thinking_data=None):
       return self.model_answers_manager.get_non_categorical_answer(prompt, topic, constrained_output, temperature, thinking_data, inference_type=self.inference_type, client=self.client, model_name=self.model_name, tokenizer=self.tokenizer, llm=self.llm, max_seq_length=self.max_seq_length)




    def calculate_options_probabilities(self, prompt, options):
        return self.model_answers_manager.calculate_options_probabilities(prompt, options, tokenizer=self.tokenizer, llm=self.llm)

    def calculate_word_probability(self, prompt, target_word, tokenizer=None, llm=None, max_seq_length=None):
        return self.model_answers_manager.calculate_word_probability(prompt, target_word, tokenizer=tokenizer, llm=llm, max_seq_length=max_seq_length)

    

    def generate_improved_prompt(self, current_prompt_text, topic_name, topic_categories_list, temperature=0.0):
        return prompt_optimizer_generate_improved_prompt(current_prompt_text, topic_name, topic_categories_list, temperature, self.prompt_model_name, self.prompt_model_type, self.prompt_inference_type, self.prompt_api_key, self.prompt_attn_implementation, self.prompt_move_to_gpu, self.prompt_device_map)



        
    def create_thinking_prompt(self, prompt, temperature, thinking_data=None):
       return prompt_optimizer_create_thinking_prompt(prompt, temperature, thinking_data, tokenizer=self.prompt_tokenizer, llm=self.prompt_llm, max_seq_length=self.prompt_max_seq_length)