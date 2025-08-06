from .config import config
from .topics import TopicsManager
from .models import ModelManager
from .helpers import MockText
from .cde_server_service import get_all_cdes, get_cde_lists_from_server, load_data_element_list_from_server, load_data_element_from_server
from .inference_server_service import InferenceServerService





class DataElementExtractor():
    def __init__(self):
        self.previous_results = {}
        self.topics_manager = TopicsManager()
        self.model_manager = ModelManager()
        self.thinking_config = {}
        self.inference_server_service = InferenceServerService()

    ### Model Management
    def set_model(self, model_name, model_type="Transformers", api_key="", inference_type="transformers", attn_implementation="flash_attention_2", move_to_gpu=True, device_map="auto"):
        self.model_manager.set_model(model_name, model_type, api_key, inference_type, attn_implementation, move_to_gpu, device_map)

    def set_prompt_model(self, model_name, model_type="OpenAI", api_key="", inference_type="cloud", attn_implementation="flash_attention_2", move_to_gpu=True, device_map="auto"):
        """Sets the model to be used for prompt generation and improvement."""
        self.model_manager.set_prompt_model(model_name, model_type, api_key, inference_type, attn_implementation, move_to_gpu, device_map)

    def set_model_as_prompt_model(self):
        self.model_manager.set_model_as_prompt_model()


    ### Topic Management
    def get_topic_by_id(self, topic_id):
        return self.topics_manager.get_topic_by_id(topic_id)

    def get_topic_id_by_name(self, topic_name):
        return self.topics_manager.get_topic_id_by_name(topic_name)

    def add_topic(self, topic_name, topic_data, condition="", prompt="", thinking_config={}):
        return self.topics_manager.add_topic(topic_name=topic_name, topic_data=topic_data, condition=condition, prompt=prompt, thinking_config=thinking_config, inference_type=self.model_manager.inference_type)

    def update_topics(self, topics):
        self.topics_manager.update_topics(topics)

    def remove_topic(self, topic_id_str):
        self.topics_manager.remove_topic(topic_id_str=topic_id_str, inference_type=self.model_manager.inference_type)
    
    def increase_topic_order(self, topic_id):
        self.topics_manager.increase_topic_order(topic_id)

    def decrease_topic_order(self, topic_id):
        self.topics_manager.decrease_topic_order(topic_id)

    def add_category(self, topicId, categoryName):
        self.topics_manager.add_category(topicId, categoryName, inference_type=self.model_manager.inference_type)

    def remove_category(self, topic_id_to_remove_from, category_id_to_remove):
        self.topics_manager.remove_category(topic_id_to_remove_from, category_id_to_remove, inference_type=self.model_manager.inference_type)

    def create_thinking_prompt(self, prompt, temperature, thinking_data=None):
        return self.model_manager.create_thinking_prompt(prompt, temperature, thinking_data)

    

    def save_topics(self, filename):
        self.topics_manager.save_topics(filename)

    def load_topics(self, filename):
        self.topics_manager.load_topics(filename)

    def show_topics_and_categories(self):
        self.topics_manager.show_topics_and_categories()

    def get_topics(self):
        return self.topics_manager.get_topics()

    def iteratively_improve_prompt(
        self, 
        topic_id, 
        dataset_path, 
        text_column_index, 
        ground_truth_column_index, 
        num_iterations=3, 
        delimiter=';'
    ):
        self.topics_manager.iteratively_improve_prompt(
            extractor_instance=self,
            topic_id=topic_id,
            dataset_path=dataset_path,
            text_column_index=text_column_index,
            ground_truth_column_index=ground_truth_column_index,
            num_iterations=num_iterations,
            delimiter=delimiter
        )


#####REDO with ExtractorInstance
    def evaluate_prompt_performance_for_topic(self, topic_id, truth_col, dataset_path, text_col=0, delimiter=';'):
        return self.topics_manager.evaluate_prompt_performance_for_topic(
            extractor_instance=self,
            topic_id=topic_id,
            truth_col=truth_col,
            dataset_path=dataset_path,
            text_col=text_col,
            delimiter=delimiter
        )

#####REDO
    def create_new_prompts_for_all_topics(self,temperature=0.0):
        for topic in self.topics_manager.get_topics():
            topic_id = topic.get('id')
            if not topic_id:
                print("Warning: Topic missing ID. Skipping improvement.")
                continue
            for cat in topic.get('categories'):
                print(cat)
                print(cat[0].value)
            new_prompt = self.model_manager.generate_improved_prompt(
                current_prompt_text=topic['prompt'].value,
                topic_name=topic['topic_input'].value,
                topic_categories_list=[cat[0].value for cat in topic.get('categories')],
                temperature=temperature
            )

            # self, current_prompt_text, topic_name, topic_categories_list
            print(f"New prompt for topic {topic_id}: {new_prompt}")
            self.set_prompt(topic_id, new_prompt)


    def set_prompt(self, topicId, newPrompt):
        self.topics_manager.set_prompt(topicId, newPrompt)


    def create_few_shot_prompt(self, topic_id, csv_path, text_col_idx, label_col_idx, delimiter=';', num_examples=3):
        self.topics_manager.create_few_shot_prompt(topic_id, csv_path, text_col_idx, label_col_idx, delimiter, num_examples)

    def create_few_shot_prompts_for_all_topics(self, csv_path, delimiter=';', num_examples=3):
        self.topics_manager.create_few_shot_prompts_for_all_topics(csv_path, delimiter, num_examples)


    def add_category_condition(self, topic_id, category_id, condition_str):
        self.topics_manager.add_category_condition(topic_id, category_id, condition_str, self.model_manager.inference_type)
    
    def remove_category_condition(self, topic_id, category_id):
        self.topics_manager.remove_category_condition(topic_id, category_id, self.model_manager.inference_type)

    def remove_all_topics(self):
        self.topics_manager.remove_all_topics(self.model_manager.inference_type)
        self.previous_results.clear()

    def evaluate_condition(self, condition):
        return self.topics_manager.evaluate_condition(condition, self.previous_results)
    
    
    

   ### Extraction
    def extract(self, text, is_single_extraction=True, constrained_output=True, with_evaluation=False, ground_truth_row=None):
        ret = []
        probs = []

        # This part of the logic for evaluation seems to only apply to categorical data.
        # A more robust implementation would be needed for evaluating non-categorical data.
        if with_evaluation and ground_truth_row is not None:
            for i, topic_info in enumerate(self.topics_manager.get_topics()):
                if (i + 1) < len(ground_truth_row):
                    ground_truth_value = ground_truth_row[i+1].strip()
                    if ground_truth_value:
                        # If the topic is categorical, the topic_data is a list of categories
                        if isinstance(topic_info.get('topic_data'), list):
                            gt_cat_id = None
                            for (cat_input, cat_id) in topic_info['categories']:
                                if cat_input.value == ground_truth_value:
                                    gt_cat_id = cat_id
                                    break
                            self.previous_results[topic_info['id']] = gt_cat_id
                        else:
                            # For non-categorical, we store the raw ground truth value for condition checking.
                            self.previous_results[topic_info['id']] = ground_truth_value
                    else:
                        self.previous_results[topic_info['id']] = None
                else:
                    self.previous_results[topic_info['id']] = None

        for topic_info in self.topics_manager.get_topics():
            condition = topic_info['condition'].value.strip()
            if not self.evaluate_condition(condition):
                ret.append("")
                probs.append(0.0)
                if is_single_extraction:
                    print(f"Skipping {topic_info['topic_input'].value} due to unmet condition: {condition}")
                continue

            # Determine the thinking configuration for this topic
            current_thinking_data = None

            # If no thinking_data is passed to classify, check the topic's config
            if 'thinking_config' in topic_info and topic_info['thinking_config']:
                current_thinking_data = topic_info['thinking_config']
            # If topic has no config, fall back to the global config
            elif self.thinking_config:
                current_thinking_data = self.thinking_config
            

            prompt_template = topic_info['prompt'].value
            # If the prompt template is empty, we use "-", since it can not be empty.
            if prompt_template == "":
                prompt_template = "-"
            topic_name = topic_info['topic_input'].value
            prompt = prompt_template.replace('[TEXT]', text).replace('[TOPIC]', topic_name)

            answer = None
            best_rel_prob = 0.0


            answer, best_rel_prob = self.extract_element(topic_info['id'], text, constrained_output, thinking_data=current_thinking_data)


            ret.append(answer)
            probs.append(best_rel_prob)

            if not with_evaluation:
                if isinstance(topic_info.get('topic_data'), list):
                    chosen_category_id = None
                    for category_input, category_id in topic_info['categories']:
                        if category_input.value == answer:
                            chosen_category_id = category_id
                            break
                    self.previous_results[topic_info['id']] = chosen_category_id
                else:
                    # For non-categorical topics, the result for condition evaluation is the extracted value itself.
                    self.previous_results[topic_info['id']] = answer
        return ret, probs

    def extract_element(self, topic_id, text, constrained_output=False, thinking_data=None):
        """
        Extracts a data element from a given text based on the topic.
        Handles both categorical and non-categorical extraction.
        """
        topic = self.get_topic_by_id(topic_id)
        answer, probability = self.model_manager.extract_element(topic, text, constrained_output, thinking_data)
        # print("Answer: ", answer)
        # print("Probability: ", probability)
        return answer, probability


    def extract_from_table(self, csv_file_path, delimiter=';', batch_size=100, with_evaluation=False, constrained_output=True):
        """
        Extracts data elements from a table (CSV file) by calling the table_extractor.

        This method avoids circular import by importing extract_from_csv_file locally.
        """
        from .table_extractor import extract_from_csv_file
        
        return extract_from_csv_file(
            dataset_path=csv_file_path,
            extractor_instance=self,
            with_evaluation=with_evaluation,
            constrained_output=constrained_output,
            batch_size=batch_size
        )




#Config Methods
    def set_choice_symbols(self, value):
        #Possible Values: "none", "alphabetical", "numerical", or a comma-separated list of custom symbols
        config.set_choice_symbol_config(value)

#Server Methods

    def get_all_cdes_from_server(self):
        return get_all_cdes()

    def get_cde_lists_from_server(self):
        return get_cde_lists_from_server()

    def load_data_element_list_from_server(self, cde_list_id):
        topics_from_list = load_data_element_list_from_server(cde_list_id)
        for topic_data in topics_from_list:

            new_topic = {
                'id': topic_data.get('id'),
                'topic_input': MockText(topic_data.get('name', '')),
                'condition': MockText(topic_data.get('condition', '')),
                'prompt': MockText(topic_data.get('prompt', '')),
                'categories': topic_data.get('categories'),
                'topic_data': topic_data.get('topic_data')
            }

            
            self.topics_manager.append_topic(new_topic)
        return self.topics_manager.get_topics()


    def load_data_element_from_server(self, cde_id):
        topics_from_list = load_data_element_from_server(cde_id)
        for topic_data in topics_from_list:

            new_topic = {
                'id': topic_data.get('id'),
                'topic_input': MockText(topic_data.get('name', '')),
                'condition': MockText(topic_data.get('condition', '')),
                'prompt': MockText(topic_data.get('prompt', '')),
                'categories': topic_data.get('categories'),
                'topic_data': topic_data.get('topic_data')
            }

            
            self.topics_manager.append_topic(new_topic)
        return self.topics_manager.get_topics()





#Config
    def set_inference_server_url(self, url):
        config.set_inference_server_url(url)
        