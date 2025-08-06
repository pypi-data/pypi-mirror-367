import csv
import os
from typing import TYPE_CHECKING
import dateparser
from transformers import StoppingCriteriaList
import re
from .helpers import StopOnTokens



def check_prompt_performance_for_topic(
    extractor_instance: 'DataElementExtractor', 
    topic_id: str, 
    dataset_path: str, 
    text_column_index: int = 0, 
    ground_truth_column_index: int = 1, 
    delimiter: str = ';'
):
    """
    Checks how well a specific topic's prompt performs on a .csv dataset.

    Args:
        extractor_instance: An instance of DataElementExtractor containing the model and topics.
        topic_id: The ID of the topic whose prompt is to be evaluated.
        dataset_path: Path to the .csv file.
        text_column_index: Index of the column containing the text to classify.
        ground_truth_column_index: Index of the column containing the ground truth category.
        constrained_output: Whether the model's output should be constrained to the given categories.
        delimiter: The delimiter used in the CSV file.
    """
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset file not found at {dataset_path}")
        return


    found_topic_config = None
    for topic_config in extractor_instance.get_topics():
        if topic_config.get('id') == topic_id:
            found_topic_config = topic_config
            break
    
    if found_topic_config is None:
        print(f"Error: No topic found with ID='{topic_id}'.")
        return

    topic_name = found_topic_config['topic_input'].value
    prompt_template = found_topic_config['prompt'].value
    # Categories in DataElementExtractor are stored as (MockText(name), MockText(condition), cat_id); only relevant for Categorical (Value List) topics
    if isinstance(found_topic_config['topic_data'], list):
        is_categorical = True
        local_categories = [
            cat_name_mock.value 
            for (cat_name_mock, _) in found_topic_config.get('categories', [])
        ]

        if not local_categories:
            print(f"Error: Topic ID='{topic_id}' has no categories defined.")
            return
    else:
        is_categorical = False
    relevant_attempts = 0
    correct_predictions = 0
    try:
        with open(dataset_path, 'r', encoding='utf-8-sig') as file: # utf-8-sig to handle potential BOM
            reader = csv.reader(file, delimiter=delimiter)
            header = next(reader, None) # Skip header row
            if header is None:
                print(f"Warning: Dataset file {dataset_path} is empty or has no header.")
                return

            rows = list(reader)
            if not rows:
                print(f"Warning: Dataset file {dataset_path} has no data rows after the header.")
                return

    except Exception as e:
        print(f"Error reading CSV file {dataset_path}: {e}")
        return

    for row_index, row in enumerate(rows):
        if not row: # Skip empty rows
            # print(f"Skipping empty row at index {row_index + 1} (after header).")
            continue

        try:
            text_to_extract = row[text_column_index].strip()
            ground_truth_answer = row[ground_truth_column_index].strip()
        except IndexError:
            # print(f"Skipping row {row_index + 1} due to missing columns. Expected at least {max(text_column_index, ground_truth_column_index) + 1} columns, got {len(row)}.")
            continue # Skip rows that don't have enough columns

        if not text_to_extract:
            # print(f"Skipping row {row_index + 1} due to empty text to extract.")
            continue 
        if not ground_truth_answer:
            # print(f"Skipping row {row_index + 1} due to empty ground truth category.")
            continue

        # Construct the prompt
        if is_categorical:
            prompt_categories_str = "[" + ",".join(f"'{cat}'" for cat in local_categories) + "]"
        else:
            prompt_categories_str = ""
        current_prompt = prompt_template.replace('[TOPIC]', topic_name)
        current_prompt = current_prompt.replace('[CATEGORIES]', prompt_categories_str)
        current_prompt = current_prompt.replace('[TEXT]', text_to_extract)
        
        # Get answer from the model via model_manager
        # Assuming extractor_instance.model_manager is accessible and has get_answer

        
        predicted_answer = extractor_instance.extract_element(
            topic_id,
            text_to_extract,
            True
        )[0]

        


        relevant_attempts += 1
         # For Date Type Topics, we need to convert the ground truth date to the same format as the prediction
        if found_topic_config['topic_data'] == 'date':
            parsed_gt_date = dateparser.parse(ground_truth_answer, settings={'DATE_ORDER': 'DMY'})
            if parsed_gt_date:
                ground_truth_answer = parsed_gt_date.strftime('%Y-%m-%d')

        print("Predicted answer: ", predicted_answer)
        print("Ground truth: ", ground_truth_answer)    
        print("Correct: ", predicted_answer == ground_truth_answer)    
        if predicted_answer == ground_truth_answer:
            correct_predictions += 1

    if relevant_attempts > 0:
        accuracy = (correct_predictions / relevant_attempts) * 100.0
        print(f"Performance for Topic '{topic_name}' (ID={topic_id}):")
        print(f"  Accuracy: {accuracy:.2f}% ({correct_predictions} correct out of {relevant_attempts} relevant attempts)")
    else:
        print(f"Performance for Topic '{topic_name}' (ID={topic_id}):")
        print("  No relevant attempts found in the dataset (e.g., missing text or ground truth data).")

    return (correct_predictions / relevant_attempts) if relevant_attempts > 0 else 0.0




def prompt_optimizer_create_thinking_prompt(prompt, temperature, thinking_data=None, tokenizer=None, llm=None, max_seq_length=None):
        """
        Creates a thinking prompt for the given topic and thinking data.
        """
        prompt_with_thinking = prompt    
        if thinking_data and thinking_data.get('think_steps'):
            for step_config in thinking_data['think_steps']:
                max_new_tokens = step_config.get('max_new_tokens', 50)
                stop_tokens = step_config.get('stop_tokens', [])
                add_text = step_config.get('add_text', '')

                stopping_criteria_list = StoppingCriteriaList()
                if stop_tokens:
                    stop_token_ids = [tok_id for t in stop_tokens for tok_id in tokenizer.encode(t, add_special_tokens=False)]
                    if stop_token_ids:
                        stopping_criteria_list.append(StopOnTokens(stop_token_ids))
                
                inputs = tokenizer(prompt_with_thinking, return_tensors="pt", truncation=True, max_length=max_seq_length).to(llm.device)
                
                generate_kwargs = {
                    "max_new_tokens": max_new_tokens,
                    "pad_token_id": tokenizer.eos_token_id
                }
                if stopping_criteria_list:
                    generate_kwargs["stopping_criteria"] = stopping_criteria_list

                if temperature > 0.0:
                    generate_kwargs["temperature"] = temperature
                    generate_kwargs["do_sample"] = True
                else:
                    generate_kwargs["do_sample"] = False

                outputs = llm.generate(**inputs, **generate_kwargs)
                new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
                generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
                prompt_with_thinking += generated_text + add_text
        return prompt_with_thinking


def prompt_optimizer_generate_improved_prompt(current_prompt_text, topic_name, topic_categories_list, temperature=0.0, prompt_model_type="Transformers", prompt_inference_type="local", prompt_model_name="", prompt_tokenizer=None, prompt_llm=None, prompt_client=None, prompt_max_seq_length=None):
    if not ((prompt_model_type == "Transformers" and prompt_llm) or 
                (prompt_inference_type == "cloud" and prompt_client)):
        print("Prompt model not configured or setup failed. Cannot generate improved prompt.")
        return current_prompt_text

    category_str = ", ".join(topic_categories_list) if topic_categories_list else "No categories defined"

    system_content = (
        f"You are an advanced prompt engineer.\n"
        f"The classification topic is '{topic_name}'.\n"
        f"The available categories for this topic are: {category_str}\n"
        "Rewrite the user's prompt to achieve higher accuracy on classification tasks.\n"
        "You MUST keep the placeholder [TEXT].\n"
        "IMPORTANT: Output ONLY the final prompt, wrapped in triple backticks (```prompt```).\n"
        "No commentary, bullet points, or explanations. The new prompt should be in English."
    )

    user_content = (
        "Here is the old prompt:\n\n"
        f"{current_prompt_text}\n\n"
        "Please rewrite/improve this prompt. Keep [TEXT]. "
        "Wrap your entire revised prompt in triple backticks, with no extra lines."
    )

    improved_prompt = current_prompt_text  # Default to old prompt

    try:
        generated_text = "" # Initialize generated_text
        if prompt_inference_type == "cloud":
            if not prompt_client:
                print("Cloud prompt client not initialized.")
                return current_prompt_text # or raise error
            completion = prompt_client.chat.completions.create(
                model=prompt_model_name,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ],
                max_tokens=300,
                temperature=temperature
            )
            generated_text = completion.choices[0].message.content.strip()
        
        elif prompt_model_type == "Transformers" and prompt_llm and prompt_tokenizer:
            full_prompt_for_llm = f"System: {system_content}\nUser: {user_content}\nAssistant:"
            inputs = prompt_tokenizer(full_prompt_for_llm, return_tensors="pt", truncation=True, max_length=prompt_max_seq_length or 512)
            
            outputs = prompt_llm.generate(
                **inputs,
                max_new_tokens=300,
                temperature=temperature,
                do_sample=True,
                pad_token_id=prompt_tokenizer.eos_token_id
            )
            # Decode only the newly generated tokens
            generated_text = prompt_tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
        else:
            print("Prompt model (Transformers) not properly initialized or missing tokenizer/LLM.")
            return current_prompt_text

        # Extract prompt from triple backticks
        match = re.search(r"```(?:[a-zA-Z]+\n)?(.*?)```", generated_text, flags=re.DOTALL)
        if match:
            extracted_prompt = match.group(1).strip()
            # The regex now handles optional language specifier like ```python\n...```
            # No need for the startswith check and split if the regex captures correctly.
            
            if "[TEXT]" in extracted_prompt:
                improved_prompt = extracted_prompt
                print(f"Successfully generated improved prompt: {improved_prompt}")
            else:
                print(f"Warning: Improved prompt generated ('{extracted_prompt}') but lacks [TEXT]. Original response: '{generated_text}'. Reverting to old prompt.")
        else:
            print(f"Warning: LLM did not provide expected triple backtick format. Full response: '{generated_text}'. Reverting to old prompt.")

    except Exception as e:
        print(f"Error during prompt generation with {prompt_model_name}: {e}")
        # improved_prompt remains current_prompt_text (its initial value)
    
    return improved_prompt