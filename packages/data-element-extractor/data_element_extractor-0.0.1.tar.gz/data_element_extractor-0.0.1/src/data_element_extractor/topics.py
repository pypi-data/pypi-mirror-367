from .inference_server_service import InferenceServerService
import re
import uuid

from .prompts import PromptManager
from .categories import CategoriesManager
from .helpers import MockText

class TopicsManager:
    def __init__(self):
        self.topics = []
        self.topic_id_counter = 0
        self.inference_server_service = InferenceServerService()
        self.categories_manager = CategoriesManager()
       

    def get_topics(self):
        return self.topics



    def add_topic(self, topic_name, topic_data, condition="", prompt="", thinking_config={}, inference_type="transformers"):
        self.topic_id_counter += 1
        topic_id = f"T{self.topic_id_counter}"
        # is_categorical is true if the topic data is a list (for a Value List Data Element)
        is_categorical = isinstance(topic_data, list)

        if not prompt:
            if topic_data=="value_list":
                prompt = (
                    "INSTRUCTION: You are a helpful classifier. You select the correct category for a piece of text. "
                    "The topic of the classification is '[TOPIC]'. The allowed categories are '[CATEGORIES]'. "
                    "QUESTION: The text to be classified is '[TEXT]'. "
                    "ANSWER: The correct category for this text is '"
                )
            elif topic_data=="number":
                prompt = (
                    "INSTRUCTION: You are a helpful extractor. You select the correct number value for the topic. The topic of the extraction is '[TOPIC]'. QUESTION: The text for the extraction is '[TEXT]'. ANSWER: The correct number value for this text is '"
                )
            elif topic_data=="date":
                prompt = (
                    "INSTRUCTION: You are a helpful extractor. You select the correct date value for the topic. The topic of the extraction is '[TOPIC]'. QUESTION: The text for the extraction is '[TEXT]'. ANSWER: The correct date value for this text is '"
                )
            elif topic_data=="text":
                prompt = (
                    "INSTRUCTION: You are a helpful extractor. You select the correct text value for the topic. The topic of the extraction is '[TOPIC]'. QUESTION: The text for the extraction is '[TEXT]'. ANSWER: The correct text value for this text is '"
                )

        new_topic = {
            'id': topic_id,
            'topic_input': MockText(topic_name),
            'categories': [],
            'condition': MockText(condition),
            'prompt': MockText(prompt),
            'topic_data': topic_data,
            'thinking_config': thinking_config
        }

        if is_categorical:
            for category_name in topic_data:
                category_id = str(uuid.uuid4())
                new_topic['categories'].append((MockText(category_name), category_id))

        self.topics.append(new_topic)
        if inference_type == "server":
            self.inference_server_service.update_topics(topics=self.topics)

        return topic_id


    def append_topic(self, topic):
        self.topics.append(topic)


    def update_topics(self, topics):
        self.topics = topics
        


    def remove_topic(self, topic_id_str, inference_type="transformers"):
        """
        Removes a topic and updates any conditions that reference it.

        Args:
            topic_id_str (str): The ID of the topic to remove.
        """
        topic_to_remove_index = -1
        topic_name_for_logging = "N/A"

        for i, topic in enumerate(self.topics):
            if topic.get('id') == topic_id_str:
                topic_to_remove_index = i
                if 'topic_input' in topic and hasattr(topic['topic_input'], 'value'):
                    topic_name_for_logging = topic['topic_input'].value
                break

        if topic_to_remove_index == -1:
            print(f"Topic with ID {topic_id_str} not found.")
            return

        # Remove the topic from the list
        del self.topics[topic_to_remove_index]
        print(f"Topic with ID '{topic_id_str}' (Name: '{topic_name_for_logging}') has been removed.")

        # Iterate through remaining topics to clean up conditions using the topic_id_str
        for other_topic in self.topics:
            condition_widget = other_topic.get('condition')

            if not condition_widget or not hasattr(condition_widget, 'value'):
                continue

            condition = condition_widget.value
            # Check if the TOPIC ID is in the condition string
            if not condition or topic_id_str not in condition:
                continue

            # Use topic_id_str for the regex, as conditions store IDs
            escaped_id_to_remove = re.escape(topic_id_str)
            
            # Comprehensive regex pattern to handle the ID with optional operators
            pattern = (
                r'\b' + escaped_id_to_remove + r'\b\s+\b(and|or)\b|'  # ID followed by 'and'/'or'
                r'\b(and|or)\b\s+\b' + escaped_id_to_remove + r'\b|'  # 'and'/'or' followed by ID
                r'\b' + escaped_id_to_remove + r'\b'                   # Standalone ID
            )
            new_condition = re.sub(pattern, '', condition, flags=re.IGNORECASE)

            # Clean up the resulting string
            new_condition = ' '.join(new_condition.split())  # Normalize whitespace
            new_condition = new_condition.replace('( )', '').replace('()', '')  # Remove empty parentheses
            new_condition = new_condition.replace('( ', '(').replace(' )', ')')  # Fix spaces around parentheses
            
            # Remove any dangling 'and'/'or' operators at the start or end
            new_condition = re.sub(r'^\s*(and|or)\b', '', new_condition, flags=re.IGNORECASE).strip()
            new_condition = re.sub(r'\b(and|or)\s*$', '', new_condition, flags=re.IGNORECASE).strip()
            new_condition = ' '.join(new_condition.split())  # Re-normalize whitespace after operator strip

            condition_widget.value = new_condition
        if inference_type == "server":
            self.inference_server_service.update_topics(topics=self.topics)


    def remove_all_topics(self, inference_type="transformers"):
        self.topics.clear()
        self.topic_id_counter = 0
        print("All topics have been removed, counters reset, and related data cleared.")
        if inference_type == "server":
            self.inference_server_service.update_topics(topics=self.topics)


    def increase_topic_order(self, topic_id):
        """Increases the order (moves up) of a topic."""
        for i, topic in enumerate(self.topics):
            if topic.get('id') == topic_id:
                if i > 0:
                    self.topics[i], self.topics[i - 1] = self.topics[i - 1], self.topics[i]
                    print(f"Topic with ID '{topic_id}' moved up.")
                else:
                    print(f"Topic with ID '{topic_id}' is already at the top.")
                return
        print(f"Topic with ID {topic_id} not found.")


    def decrease_topic_order(self, topic_id):
        """Decreases the order (moves down) of a topic."""
        for i, topic in enumerate(self.topics):
            if topic.get('id') == topic_id:
                if i < len(self.topics) - 1:
                    self.topics[i], self.topics[i + 1] = self.topics[i + 1], self.topics[i]
                    print(f"Topic with ID '{topic_id}' moved down.")
                else:
                    print(f"Topic with ID '{topic_id}' is already at the bottom.")
                return
        print(f"Topic with ID {topic_id} not found.")




    def add_category(self, topicId, categoryName, inference_type="transformers"):
        self.categories_manager.add_category(self.topics, topicId, categoryName)
        if inference_type == "server":
            self.inference_server_service.update_topics(topics=self.topics)


    def remove_category(self, topic_id_to_remove_from, category_id_to_remove, inference_type="transformers"):
        topic_to_remove_from = self.get_topic_by_id(topic_id_to_remove_from)
        self.categories_manager.remove_category(self.topics, topic_to_remove_from, category_id_to_remove, inference_type)
        if inference_type == "server":
            self.inference_server_service.update_topics(topics=self.topics)



    def get_topic_by_id(self, topic_id):
        """Finds and returns a topic dictionary by its ID."""
        for topic in self.topics:
            if topic.get('id') == topic_id:
                return topic
        return None


    def clear(self):
        self.topics.clear()



    def save_topics(self, filename):
        from .helpers import serialize_topics
        from .persistence import save_data_to_json
        data = serialize_topics(self.topics)
        save_data_to_json(data, filename)


    def load_topics(self, filename):
        from .persistence import load_data_from_json
        data = load_data_from_json(filename)
        if data is None:
            # Error/file not found messages are handled by load_data_from_json
            return

        self.topics.clear()
        max_topic_num = 0

        for topic_data in data:
            new_topic = {
                'id': topic_data.get('id', ''),
                'topic_input': MockText(topic_data.get('topic_input', '')),
                'topic_data': topic_data.get('topic_data', ''),
                'condition': MockText(topic_data.get('condition', '')),
                'prompt': MockText(topic_data.get('prompt', '')),
                'thinking_config': topic_data.get('thinking_config', {}),
                'categories': []
            }

            for cat_dict in topic_data.get('categories', []):
                cat_id = cat_dict.get('id', '')
                cat_name = cat_dict.get('name', '')  # Expect 'name' key
                new_topic['categories'].append(
                    (MockText(cat_name), cat_id)
                )
            
            self.append_topic(new_topic)
            
            # Update topic counter
            topic_id_str = new_topic['id']
            if topic_id_str.startswith('T'):
                try:
                    topic_num = int(topic_id_str[1:])
                    if topic_num > max_topic_num:
                        max_topic_num = topic_num
                except ValueError:
                    pass # Ignore if the part after 'T' is not a number
        
        self.topic_id_counter = max_topic_num
        print(f"Topics loaded from {filename}")



    def show_topics_and_categories(self):
        if not self.topics:
            print("No topics are currently defined.")
            return

        for i, topic_info in enumerate(self.topics, start=1):
            topic_name = topic_info['topic_input'].value
            topic_id = topic_info.get('id', '?')
            
            condition_val = topic_info['condition'].value if 'condition' in topic_info else None
            prompt_val = topic_info['prompt'].value if 'prompt' in topic_info else None

            print(f"Topic {i} (ID={topic_id}): {topic_name}")

            if condition_val:
                print(f"  Condition: {condition_val}")

            if prompt_val:
                print(f"  Prompt: {prompt_val}")

            categories = topic_info.get('categories', [])
            if not categories:
                print("    [No categories in this topic]")
            else:
                for j, (cat_name_mock, cat_id) in enumerate(categories, start=1):
                    cat_name = cat_name_mock.value
                    display_str = f"    {j}. {cat_name} (ID={cat_id})"
                    print(display_str)



    ### Prompt Management ###
    def iteratively_improve_prompt(
        self, 
        extractor_instance,
        topic_id, 
        dataset_path, 
        text_column_index, 
        ground_truth_column_index, 
        num_iterations=3, 
        delimiter=';'
    ):
        topic = self.get_topic_by_id(topic_id)
        if not topic:
                print(f"Error: Topic with ID {topic_id} not found.")
                return
        self.prompt_manager.iteratively_improve_prompt(
            extractor_instance=extractor_instance,
            topics=self.topics,
            topic=topic,
            dataset_path=dataset_path,
            text_column_index=text_column_index,
            ground_truth_column_index=ground_truth_column_index,
            num_iterations=num_iterations,
            delimiter=delimiter
        )

    def evaluate_prompt_performance_for_topic(self, extractor_instance, topic_id, truth_col, dataset_path, text_col=0, delimiter=';'):
       self.prompt_manager.evaluate_prompt_performance_for_topic(
            extractor_instance=extractor_instance,
            topic_id=topic_id,
            truth_col=truth_col,
            dataset_path=dataset_path,
            text_col=text_col,
            delimiter=delimiter
        )

    def set_prompt(self, topicId, newPrompt):
        self.prompt_manager.set_prompt(self.topics, topicId, newPrompt)


    def create_few_shot_prompt(self, topic_id, csv_path, text_col_idx, label_col_idx, delimiter=';', num_examples=3):
        topic = self.get_topic_by_id(topic_id)
        if not topic:
            print(f"Error: Topic with ID {topic_id} not found.")
            return
        self.prompt_manager.create_few_shot_prompt(
            topic_id=topic_id,
            csv_path=csv_path,
            text_col_idx=text_col_idx,
            label_col_idx=label_col_idx,
            delimiter=delimiter,
            num_examples=num_examples
        )

    def create_few_shot_prompts_for_all_topics(self, csv_path, delimiter=';', num_examples=3):
        self.prompt_manager.create_few_shot_prompts_for_all_topics(
            topics=self.topics,
            csv_path=csv_path,
            delimiter=delimiter,
            num_examples=num_examples
        )


    ### Category Manager
    def add_category_condition(self, topic_id, category_id, condition_str, inference_type="transformers"):
        self.categories_manager.add_category_condition(
            topics=self.topics,
            topic_id=topic_id,
            category_id=category_id,
            condition_str=condition_str
        )
        if inference_type == "server":
            self.inference_server_service.update_topics(topics=self.topics)


    def remove_category_condition(self, topic_id, category_id, inference_type="transformers"):
        self.categories_manager.remove_category_condition(
            topics=self.topics,
            topic_id=topic_id,
            category_id=category_id
        )
        if inference_type == "server":
            self.inference_server_service.update_topics(topics=self.topics)





    def evaluate_condition(self, condition, previous_results):
        return self.categories_manager.evaluate_condition(condition, previous_results)





    def get_topic_id_by_name(self, topic_name):
        for topic in self.topics:
            if topic['topic_input'].value == topic_name:
                return topic['id']
        return None