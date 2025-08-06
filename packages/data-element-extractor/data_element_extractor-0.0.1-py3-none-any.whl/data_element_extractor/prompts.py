from .prompt_optimizer import check_prompt_performance_for_topic # For iterative improvement
import csv
from .helpers import MockText

class PromptManager:
    def __init__(self):
        pass


    def iteratively_improve_prompt(
            self,
            extractor_instance,
            topics, 
            topic,
            dataset_path, 
            text_column_index, 
            ground_truth_column_index, 
            num_iterations=3, 
            delimiter=';'
        ):
            """Iteratively improves the prompt for a given topic using a prompt model."""
            print(f"\n--- Starting Iterative Prompt Improvement for Topic ID: {topic.get('id')} ---")
            # self.set_prompt_model(prompt_model_name, prompt_model_type, prompt_api_key, prompt_inference_type)

            topic_name = topic['topic_input'].value
            topic_id = topic['id']
            topic_categories = [cat[0].value for cat in topic.get('categories', [])]

            best_prompt_text = topic['prompt'].value
            # Initial accuracy check for the starting prompt
            print(f"Initial prompt for '{topic_name}': {best_prompt_text}")
            best_accuracy = check_prompt_performance_for_topic(
                extractor_instance=extractor_instance,
                topic_id=topic_id,
                dataset_path=dataset_path,
                text_column_index=text_column_index,
                ground_truth_column_index=ground_truth_column_index,
                delimiter=delimiter
            )
            if best_accuracy is None: # check_prompt_performance_for_topic returns None on error
                print(f"Error evaluating initial prompt for topic {topic_id}. Aborting improvement process.")
                return
            print(f"Initial accuracy: {best_accuracy:.2f}%")

            for i in range(num_iterations):
                print(f"\n--- Iteration {i + 1} of {num_iterations} ---")
                current_prompt_text = topic['prompt'].value # Get current prompt from topic

                print(f"Attempting to improve prompt: {current_prompt_text}")
                new_prompt_text = extractor_instance.model_manager.generate_improved_prompt(
                    current_prompt_text=current_prompt_text,
                    topic_name=topic_name,
                    topic_categories_list=topic_categories
                )

                if new_prompt_text == current_prompt_text or "[TEXT]" not in new_prompt_text:
                    print("No improvement or invalid prompt generated. Keeping current best prompt.")
                    continue # Skip to next iteration or finish if no better prompt is found

                # Update topic with the new prompt for evaluation
                self.set_prompt(topics, topic_id, new_prompt_text)
                print(f"Evaluating new prompt: {new_prompt_text}")
                current_iteration_accuracy = check_prompt_performance_for_topic(
                    extractor_instance=extractor_instance,
                    topic_id=topic_id,
                    dataset_path=dataset_path,
                    text_column_index=text_column_index,
                    ground_truth_column_index=ground_truth_column_index,
                    delimiter=delimiter
                )

                if current_iteration_accuracy is None:
                    print(f"Error evaluating new prompt in iteration {i+1}. Reverting to previous best prompt.")
                    self.set_prompt(topics, topic_id, best_prompt_text) # Revert to best known good prompt
                    continue
                
                print(f"New prompt accuracy: {current_iteration_accuracy:.2f}%")

                if current_iteration_accuracy > best_accuracy:
                    print(f"Improvement found! Accuracy: {current_iteration_accuracy:.2f}% > {best_accuracy:.2f}%")
                    best_accuracy = current_iteration_accuracy
                    best_prompt_text = new_prompt_text
                    # The topic's prompt is already set to new_prompt_text, so it's the new best.
                else:
                    print(f"No improvement in accuracy ({current_iteration_accuracy:.2f}% <= {best_accuracy:.2f}%). Reverting to previous best prompt.")
                    self.set_prompt(topics, topic_id, best_prompt_text) # Revert to the known best prompt
            
            # Ensure the topic is set to the overall best prompt found
            self.set_prompt(topics, topic_id, best_prompt_text)
            print(f"\n--- Iterative Prompt Improvement Finished for Topic ID: {topic_id} ---")
            print(f"Best prompt found: {best_prompt_text}")
            print(f"Best accuracy achieved: {best_accuracy:.2f}%")



    def evaluate_prompt_performance_for_topic(self, extractor_instance, topic_id, truth_col, dataset_path, text_col=0, delimiter=';'):
        text_col, truth_col = int(text_col), int(truth_col)
        return check_prompt_performance_for_topic(
            extractor_instance=extractor_instance,
            topic_id=topic_id,
            dataset_path=dataset_path,
            text_column_index=text_col,
            ground_truth_column_index=truth_col,
            delimiter=delimiter
        )



    def set_prompt(self, topics, topicId, newPrompt):
        for topic in topics:
            if topic.get('id') == topicId:
                if 'prompt' in topic and hasattr(topic['prompt'], 'value'):
                    topic['prompt'].value = newPrompt
                else:
                    topic['prompt'] = MockText(newPrompt)
                print(f"Prompt for topic ID {topicId} updated.")
                return
        print(f"Topic with ID {topicId} not found.")





    def create_few_shot_prompt(self, topic, csv_path, text_col_idx, label_col_idx, delimiter=';', num_examples=3):
        """
        Creates and sets a few-shot prompt for a topic based on examples from a CSV file.

        Args:
            topic (dict): The topic dictionary to update.
            csv_path (str): The path to the CSV file with labeled data.
            text_col_idx (int): The index of the column containing the text.
            label_col_idx (int): The index of the column containing the label.
            delimiter (str): The delimiter used in the CSV file.
            num_examples (int): The number of examples to include in the prompt.
        """
        topic_id = topic['id']
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=delimiter)
                header = next(reader)  # Skip header
                examples = [row for row in reader if row]
        except FileNotFoundError:
            print(f"Error: File not found at {csv_path}")
            return
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return

        base_prompt = topic['prompt'].value+"[ANSWER]"
        # Find the main instruction part by splitting at the 'QUESTION:' part
        parts = base_prompt.split("QUESTION:")
        if len(parts) < 2:
            print("Error: The base prompt does not seem to have the 'QUESTION:' separator.")
            return

        instruction_part = parts[0]
        final_question_part = "QUESTION:" + parts[-1]

        # Filter for rows that have a valid, non-empty label for the given column index
        valid_examples = [
            row for row in examples 
            if len(row) > label_col_idx and row[label_col_idx] and row[label_col_idx].strip()
        ]

        if not valid_examples:
            print(f"Warning: No valid examples found for topic {topic_id} with label column {label_col_idx}. Prompt not updated.")
            return

        few_shot_examples = []
        # Take the first `num_examples` from the valid list
        for row in valid_examples[:num_examples]:
            if len(row) > text_col_idx:
                text = row[text_col_idx]
                label = row[label_col_idx]
                # We need to reconstruct the example from the final question part
                example_prompt = final_question_part.replace("[TEXT]", f"'{text}'.")
                example_prompt = example_prompt.replace("[ANSWER]", f"is '{label}'")
                few_shot_examples.append(example_prompt)

        if not few_shot_examples:
            print("Warning: No examples were generated. The prompt was not updated.")
            return

        # Combine instruction, examples, and the final question
        new_prompt = instruction_part + "\n".join(few_shot_examples) + "\n" + final_question_part
        
        self.set_prompt(topic_id, new_prompt)
        print(f"Few-shot prompt created and set for topic {topic_id} with {len(few_shot_examples)} examples.")



    def create_few_shot_prompts_for_all_topics(self, topics, csv_path, delimiter=';', num_examples=3):
        """
        Creates few-shot prompts for all topics based on a single CSV file.

        It assumes the text column is at index 0, and the label for each topic
        corresponds to the subsequent columns (topic 1 -> col 1, topic 2 -> col 2, etc.).
        """
        print(f"Starting to create few-shot prompts for all topics from '{csv_path}'...")
        for i, topic in enumerate(topics):
            topic_id = topic['id']
            topic_name = topic['topic_input'].value
            label_col_idx = i + 1  # Text is col 0, labels start from col 1

            print(f"  - Creating prompt for topic '{topic_name}' (ID: {topic_id}) using label column {label_col_idx}.")
            
            self.create_few_shot_prompt(
                topic_id=topic_id,
                csv_path=csv_path,
                text_col_idx=0,
                label_col_idx=label_col_idx,
                delimiter=delimiter,
                num_examples=num_examples
            )
        print("Finished creating few-shot prompts for all topics.")
