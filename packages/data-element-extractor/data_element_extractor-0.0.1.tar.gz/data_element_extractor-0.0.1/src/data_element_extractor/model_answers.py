from .config import config
from .helpers import generate_symbols, serialize_topics, StopOnTokens
from .inference_server_service import InferenceServerService
from transformers import StoppingCriteriaList
from .number_logits_processor import NumberLogitsProcessor
import re
import torch
import dateparser
import json
from .prompt_optimizer import prompt_optimizer_create_thinking_prompt




class ModelAnswersManager:
    def __init__(self):
       self.inference_server_service = InferenceServerService()


    def extract_element(self, topic, text, constrained_output=False, inference_type="transformers", thinking_data=None, tokenizer=None, llm=None, max_seq_length=None):
        if not topic:
            return None
        prompt_template = topic['prompt'].value
        topic_name = topic['topic_input'].value
        prompt = prompt_template.replace("[TEXT]", text).replace("[TOPIC]", topic_name)

        if isinstance(topic.get('topic_data'), list):
            categories = [cat[0].value for cat in topic['categories']]
            symbol_config = config.get_choice_symbol_config()
            symbols = generate_symbols(symbol_config, len(categories))

            if symbols:
                # Format as "A: category1, B: category2, ..."
                formatted_categories = ", ".join([f"{symbols[i]}: {cat}" for i, cat in enumerate(categories)])
            else:
                # Format as "category1, category2, ..."
                formatted_categories = ", ".join(categories)
            prompt = prompt.replace("[CATEGORIES]", formatted_categories)
            extracted_data, probability = self.get_answer(prompt, categories=categories, constrained_output=True, inference_type=inference_type, thinking_data=thinking_data, tokenizer=tokenizer, llm=llm, max_seq_length=max_seq_length)
        else:
            extracted_data, probability = self.get_non_categorical_answer(prompt, topic, constrained_output=constrained_output, inference_type=inference_type, thinking_data=thinking_data, tokenizer=tokenizer, llm=llm, max_seq_length=max_seq_length)
            # self.get_non_categorical_answer(prompt, topic, constrained_output=constrained_output, thinking_data=thinking_data)
            probability = 1.0
        return extracted_data, probability









    def get_answer(self, prompt, categories, constrained_output, temperature=0.0, thinking_data=None, inference_type="transformers", client=None, model_name="", tokenizer=None, llm=None, max_seq_length=None):
        if prompt == "":
            prompt = "-"


        if inference_type == "server":
            server_answer = self.inference_server_service.get_answer(prompt, categories, constrained_output, temperature, thinking_data)
            return server_answer['answer'], server_answer['probability']

        elif inference_type == "cloud":
            # The thinking steps for cloud models are not implemented in this version.
            # It would require a different approach, likely involving multiple API calls
            # and careful prompt engineering to simulate a step-by-step thinking process.
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=30,
                temperature=temperature,
            )
            generated_answer = completion.choices[0].message.content.strip()

            print("Generated answer: ", generated_answer)
            endOfThinkingString="</think>"
            #Copy only the text after the endOfThinkingString
            generated_answer = generated_answer.split(endOfThinkingString)[1].strip()
            print("Generated answer after thinking: ", generated_answer)
            
            for option in categories:
                escaped_option = re.escape(option)
                if re.search(escaped_option, generated_answer, re.IGNORECASE):
                    return option, "-"
            return "undefined", "-"

        elif inference_type == "transformers":
            prompt_with_thinking = prompt
            if thinking_data and thinking_data.get('think_steps'):
                for step_config in thinking_data['think_steps']:
                    max_new_tokens = step_config.get('max_new_tokens', 50)
                    stop_tokens = step_config.get('stop_tokens', [])
                    add_text = step_config.get('add_text', '')

                    stopping_criteria_list = StoppingCriteriaList()
                    if stop_tokens:
                        # `encode` can return a list of tokens for a single string
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
                    print(prompt_with_thinking)      
            # The final prompt for answer generation includes the thinking process
            final_prompt = prompt_with_thinking

            if constrained_output:
                best_option, _, _, _, best_rel_prob = self.calculate_options_probabilities(final_prompt, categories, tokenizer=tokenizer, llm=llm, max_seq_length=max_seq_length)
                return best_option, best_rel_prob
            else:
                # Generate a free-form answer after thinking
                inputs = tokenizer(final_prompt, return_tensors="pt", truncation=True, max_length=max_seq_length).to(llm.device)
                
                generate_kwargs = {
                    "max_new_tokens": 30, # For the final answer
                    "pad_token_id": tokenizer.eos_token_id
                }
                if temperature > 0.0:
                    generate_kwargs["temperature"] = temperature
                    generate_kwargs["do_sample"] = True
                else:
                    generate_kwargs["do_sample"] = False

                outputs = llm.generate(**inputs, **generate_kwargs)
                new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
                generated_answer = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
                
                # In free-form, we still try to match categories from the generated answer
                for option in categories:
                    # Use word boundaries to avoid matching substrings inside words
                    if re.search(r'\b' + re.escape(option) + r'\b', generated_answer, re.IGNORECASE):
                        return option, "-"
                
                # If no category is matched, we can decide what to return.
                # Returning "undefined" is consistent with other parts of the function.
                return "undefined", "-"

        elif inference_type == "server":
            answer, probability = self.inference_server_service.get_answer(prompt, categories, constrained_output, temperature, thinking_data)
            print(answer)
            print(probability)
            return answer, probability

        return "undefined", "-"


    def get_non_categorical_answer(self, prompt, topic, constrained_output, temperature=0.0, thinking_data=None, inference_type="transformers", client=None, model_name="", tokenizer=None, llm=None, max_seq_length=None):
        """
        Gets an answer for non-categorical topics, with optional constraints.
        """
        
        if inference_type == "server":
            serialized_topic = serialize_topics([topic])[0]
            return self.inference_server_service.get_non_categorical_answer(prompt=prompt, topic=serialized_topic, constrained_output=constrained_output, temperature=temperature, thinking_data=thinking_data)

        topic_data_type = topic.get('topic_data')

        if constrained_output:
            if topic_data_type == 'number':
                if inference_type == "cloud":
                    tools = [{"type": "function", "function": {"name": "submit_extracted_number", "description": "Submit the numerical value extracted from the text.", "parameters": {"type": "object", "properties": {"value": {"type": "number", "description": "The numerical value that was extracted."}}, "required": ["value"]}}}]
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": "You are an assistant that extracts numerical data."}, {"role": "user", "content": prompt}],
                        tools=tools,
                        tool_choice={"type": "function", "function": {"name": "submit_extracted_number"}},
                    )
                    response_message = completion.choices[0].message
                    if response_message.tool_calls:
                        function_args = json.loads(response_message.tool_calls[0].function.arguments)
                        return str(function_args.get("value"))
                    return None, None
                elif inference_type == "transformers":
                    # print("Thinking...")
                    prompt = prompt_optimizer_create_thinking_prompt(prompt, temperature, thinking_data, tokenizer=tokenizer, llm=llm, max_seq_length=max_seq_length)
                    # print(prompt)
                    inputs = tokenizer(prompt, return_tensors="pt")
                    inputs = inputs.to(llm.device)
                    logits_processor = NumberLogitsProcessor(tokenizer, inputs)
                    outputs = llm.generate(**inputs, max_new_tokens=10, pad_token_id=tokenizer.eos_token_id, logits_processor=[logits_processor])
                    decoded_output = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
                    
                    # Take the part before any space
                    number_part = decoded_output.split(' ')[0]
                    
                    # Clean up the number format
                    try:
                        num = float(number_part)
                        if num.is_integer():
                            return str(int(num)), 1.0
                        else:
                            return str(num), 1.0
                    except ValueError:
                        # Fallback if conversion fails, though LogitsProcessor should prevent this
                        return number_part, 1.0
            elif topic_data_type == 'date':
                # print("Thinking...")
                prompt = prompt_optimizer_create_thinking_prompt(prompt, temperature, thinking_data, tokenizer=tokenizer, llm=llm, max_seq_length=max_seq_length)
                # print(prompt)
                inputs = tokenizer(prompt, return_tensors="pt")
                inputs = inputs.to(llm.device)
                outputs = llm.generate(**inputs, max_new_tokens=50, pad_token_id=tokenizer.eos_token_id)
                raw_extracted_data = tokenizer.decode(outputs[0], skip_special_tokens=True)[len(prompt):].strip()
                print(raw_extracted_data)
                if inference_type == "transformers":
                    # The LLM output can be messy. First, we use a regex to find a clean,
                    # numeric date string like 'DD.MM.YYYY'. This is more reliable than parsing the whole output.
                    date_pattern = r'\b(\d{4}[.-]\d{1,2}[.-]\d{1,2}|\d{1,2}[.-]\d{1,2}[.-]\d{4}|\d{1,2}[.-]\d{4})\b'
                    match = re.search(date_pattern, raw_extracted_data)

                    if match:
                        date_string = match.group(0)
                        # Now that we have a clean string, parse it.
                        # DATE_ORDER='YMD' is crucial for formats like '2024-08-22'.
                        parsed_date = dateparser.parse(date_string, settings={'DATE_ORDER': 'YMD'})
                        if parsed_date:
                            print(parsed_date.strftime('%Y-%m-%d'))
                            return parsed_date.strftime('%Y-%m-%d'), 1.0
                        # DATE_ORDER='DMY' is crucial for formats like '22.08.2024'.
                        parsed_date = dateparser.parse(date_string, settings={'DATE_ORDER': 'DMY'})
                        if parsed_date:
                            print(parsed_date.strftime('%Y-%m-%d'))
                            return parsed_date.strftime('%Y-%m-%d'), 1.0    
                        # DATE_ORDER='MDY' is crucial for formats like '08-22-2024'.
                        parsed_date = dateparser.parse(date_string, settings={'DATE_ORDER': 'MDY'})
                        if parsed_date:
                            print(parsed_date.strftime('%Y-%m-%d'))
                            return parsed_date.strftime('%Y-%m-%d'), 1.0
                            

                    # If regex fails, we can't be sure about the format, so we return None
                    # to avoid incorrect extractions.
                    return None, None
                elif inference_type == "cloud":
                    tools = [{"type": "function", "function": {"name": "submit_extracted_date", "description": "Submit the date extracted from the text.", "parameters": {"type": "object", "properties": {"date": {"type": "string", "description": "The extracted date in YYYY-MM-DD format."}}, "required": ["date"]}}}]
                    completion = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": "You are an assistant that extracts date information."}, {"role": "user", "content": prompt}],
                        tools=tools,
                        tool_choice={"type": "function", "function": {"name": "submit_extracted_date"}},
                    )
                    response_message = completion.choices[0].message
                    if response_message.tool_calls:
                        function_args = json.loads(response_message.tool_calls[0].function.arguments)
                        return function_args.get("date"), 1.0
                    return None, None

        # Default behavior (unconstrained, or local-constrained-date)
        raw_extracted_data = ""
        if inference_type == "cloud":
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
                max_tokens=50, temperature=0.0)
            raw_extracted_data = completion.choices[0].message.content.strip()
        elif inference_type == "transformers":
            inputs = tokenizer(prompt, return_tensors="pt")
            inputs = inputs.to(llm.device)
            outputs = llm.generate(**inputs, max_new_tokens=50, pad_token_id=tokenizer.eos_token_id)
            raw_extracted_data = tokenizer.decode(outputs[0], skip_special_tokens=True)[len(prompt):].strip()
        if topic_data_type == 'number':
            potential_numbers = re.findall(r'-?\d+\.?\d*|-?\.\d+', raw_extracted_data)
            for num_str in potential_numbers:
                try:
                    float(num_str)
                    return num_str, 1.0
                except ValueError:
                    continue
            return None, None
        elif topic_data_type == 'date':
            # The LLM output can be messy. First, we use a regex to find a clean,
            # numeric date string like 'DD.MM.YYYY'. This is more reliable than parsing the whole output.
            date_pattern = r'\b(\d{1,2}[./-]\d{1,2}[./-]\d{4})\b'
            match = re.search(date_pattern, raw_extracted_data)

            if match:
                date_string = match.group(0)
                # Now that we have a clean string, parse it.
                # DATE_ORDER='DMY' is crucial for formats like '22.08.2024'.
                parsed_date = dateparser.parse(date_string, settings={'DATE_ORDER': 'DMY'})
                if parsed_date:
                    return parsed_date.strftime('%Y-%m-%d'), 1.0

            # If regex fails, we can't be sure about the format, so we return None
            # to avoid incorrect extractions.
            return None, None

        elif topic_data_type == 'text':
            # For 'text' type, we return the raw, unprocessed output from the LLM.
            return raw_extracted_data, 1.0

        # Fallback for any other undefined non-categorical types
        return raw_extracted_data, 1.0




    def calculate_options_probabilities(self, prompt, options, tokenizer=None, llm=None, max_seq_length=None):
        llm.eval()
        space_prefix = ' ' if not prompt.endswith(' ') else ''
        
        first_token_groups = {}
        # print("Options: ", options)
        for option in options:
            first_token = tokenizer.encode(space_prefix + option, add_special_tokens=False)[0]
            if first_token not in first_token_groups:
                first_token_groups[first_token] = []
            first_token_groups[first_token].append(option)
            
        base_inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=max_seq_length)
        base_inputs = {k: v.to(llm.device) for k, v in base_inputs.items()}

        option_probabilities = {}
        with torch.no_grad():
            base_outputs = llm(**base_inputs)
            base_logits = base_outputs.logits[0, -1, :]
            base_probs = torch.nn.functional.softmax(base_logits, dim=-1)
            
        for first_token_id, group_options in first_token_groups.items():
            if len(group_options) == 1:
                option = group_options[0]
                token_ids = tokenizer.encode(space_prefix + option, add_special_tokens=False)
                
                if len(token_ids) == 1:
                    option_probabilities[option] = base_probs[first_token_id].item()
                else:
                    probability, _ = self.calculate_word_probability(prompt, option, tokenizer, llm, max_seq_length)
                    option_probabilities[option] = probability
            else:
                for option in group_options:
                    probability, _ = self.calculate_word_probability(prompt, option, tokenizer, llm, max_seq_length)
                    option_probabilities[option] = probability
        
        total_probability = sum(option_probabilities.values())
        relative_probabilities = {
            option: (prob / total_probability if total_probability > 0 else 0)
            for option, prob in option_probabilities.items()
        }
        
        best_option = max(option_probabilities.items(), key=lambda x: x[1])
        
        return best_option[0], best_option[1], option_probabilities, relative_probabilities, relative_probabilities[best_option[0]]



    def calculate_word_probability(self, prompt, target_word, tokenizer=None, llm=None, max_seq_length=None):
        llm.eval()
        target_word_with_space = ' ' + target_word if not prompt.endswith(' ') else target_word
        target_tokens = tokenizer.encode(target_word_with_space, add_special_tokens=False)
        token_probabilities = []
        current_text = prompt

        for token_id in target_tokens:
            inputs = tokenizer(current_text, return_tensors="pt", truncation=True, max_length=max_seq_length)
            inputs = {k: v.to(llm.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = llm(**inputs)
            next_token_logits = outputs.logits[0, -1, :]
            next_token_probs = torch.nn.functional.softmax(next_token_logits, dim=-1)
            token_prob = next_token_probs[token_id].item()
            token_probabilities.append(token_prob)
            current_text = tokenizer.decode(
                tokenizer.encode(current_text, add_special_tokens=False) + [token_id],
                skip_special_tokens=True
            )
        total_probability = torch.tensor(token_probabilities).prod().item()

        return total_probability, token_probabilities



    



    