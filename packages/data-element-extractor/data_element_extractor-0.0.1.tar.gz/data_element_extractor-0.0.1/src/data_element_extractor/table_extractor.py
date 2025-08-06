import csv
import os
import time
import dateparser
from .extractor import DataElementExtractor

# Placeholder for topics, will be managed by Extractor instance
# topics = [] 

# Placeholder for model, will be managed by Extractor instance
# LLM = None 

def get_header_list(extractor_instance):
    """Generates headers for the output CSV based on the extractor's topics."""
    # Uses the get_header_list method from the Extractor instance
    return extractor_instance.get_header_list()

def process_batch(extractor_instance, batch_rows, start_index, with_evaluation=False, constrained_output=True):
    """Process a batch of rows using the provided Extractor instance."""
    batch_results = []
    batch_probs = []
    batch_indices = []
    for idx, row in enumerate(batch_rows):
        actual_index = start_index + idx
        # Assuming the first column of the row is the text to classify
        text_to_classify = row[0]
        
        result, probs = extractor_instance.extract(
            text_to_classify,
            is_single_extraction=False, # Important for table context
            constrained_output=constrained_output,
            with_evaluation=with_evaluation,
            ground_truth_row=row if with_evaluation else None
        )
        batch_results.append(result)
        batch_probs.append(probs)
        batch_indices.append(actual_index)
    return batch_results, batch_probs, batch_indices

def process_and_write_result(count, row, result, prob, save_name, with_evaluation, 
                           extractor_instance, category_confusions):
    """Helper function to process and write a single result, and update evaluation metrics."""
    # This function will be more complex and needs careful adaptation of logic 
    # from previous_code.py, especially regarding how topics and categories 
    # are accessed via extractor_instance.

    # Update confusion matrices
    # The structure of 'topics' in Extractor is slightly different.
    # topics is a list of dicts, each dict has 'categories' which is a list of tuples.
    # (MockText(category_name), MockText(condition), category_id)

    topics_data = extractor_instance.get_topics() # Access topics from the instance

    for t_index, pred_category_name in enumerate(result):
        if with_evaluation and (t_index + 1) < len(row):
            ground_truth_category_name = row[t_index + 1].strip()
            if ground_truth_category_name: # Ensure there's a ground truth to compare against
                # Only update confusion matrix for categorical topics, which are pre-initialized
                if t_index in category_confusions:
                    current_topic_categories = topics_data[t_index]['categories']
                    # Update TP, FP, FN, TN for each category in the current topic
                    for cat_tuple in current_topic_categories:
                        cat_name = cat_tuple[0].value
                        conf_map = category_confusions[t_index][cat_name]
                        if cat_name == ground_truth_category_name and cat_name == pred_category_name:
                            conf_map["TP"] += 1
                        elif cat_name != ground_truth_category_name and cat_name == pred_category_name:
                            conf_map["FP"] += 1
                        elif cat_name == ground_truth_category_name and cat_name != pred_category_name:
                            conf_map["FN"] += 1
                        elif cat_name != ground_truth_category_name and cat_name != pred_category_name:
                            conf_map["TN"] += 1

    # Prepare result row for CSV
    single_result_row = [str(count), row[0]]
    # numberOfCorrectResults and numberOfRelevantAttempts will be managed in the main classify_csv_file function

    for t_index, pred_category_name in enumerate(result):
        # Get the probability for the current prediction
        # The probs list from extractor.extract_element corresponds to each topic's prediction
        current_prob = prob[t_index] if t_index < len(prob) else ""

        if with_evaluation and (t_index + 1) < len(row):
            ground_truth_category_name = row[t_index + 1].strip()
            single_result_row.append(ground_truth_category_name) # Ground Truth
            single_result_row.append(pred_category_name)       # Predicted
            single_result_row.append(str(current_prob))        # Probability
        else:
            single_result_row.append(pred_category_name)       # Predicted
            single_result_row.append(str(current_prob))        # Probability

    # Write to file
    with open(save_name + ".csv", 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(single_result_row)


def extract_from_csv_file(dataset_path, extractor_instance: DataElementExtractor, 
                      with_evaluation=False, constrained_output=True, batch_size=100, progress_callback=None):
    """Classifies text from a CSV file and optionally evaluates the results."""
    start_time = time.time()
    
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset file not found at {dataset_path}")
        return

    # categoryConfusions will be a dict mapping topic_index to its confusion_map
    # e.g., {0: {'catA': {'TP':0,...}, 'catB':{...}}, 1: {'catC':{...}}}
    category_confusions = {}
    for i, topic in enumerate(extractor_instance.get_topics()):
        topic_type = topic.get('topic_data')
        # A topic is categorical if its data is not a string (e.g., 'date', 'text').
        # It's usually a list for categorical topics.
        if not isinstance(topic_type, str):
            category_confusions[i] = {}
            for cat_tuple in topic['categories']:
                cat_name = cat_tuple[0].value
                category_confusions[i][cat_name] = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
    
    # These will be lists, indexed by topic index
    num_correct_results_per_topic = [0] * len(extractor_instance.get_topics())
    num_relevant_attempts_per_topic = [0] * len(extractor_instance.get_topics())
    per_topic_eval_data = [[] for _ in extractor_instance.get_topics()] # To store (prob, is_correct)

    base_name, _ = os.path.splitext(dataset_path)
    save_name = base_name + "_(result)"

    try:
        with open(dataset_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';') # Assuming semicolon delimiter as in previous_code
            reader_list = list(reader)
            if not reader_list:
                print(f"Error: CSV file {dataset_path} is empty or could not be read.")
                return
    except Exception as e:
        print(f"Error reading CSV file {dataset_path}: {e}")
        return

    # Prepare header for the output file
    output_header = ["RowID", "Text"] # Start with RowID and Text
    topics_data = extractor_instance.get_topics()
    for topic_info in topics_data:
        topic_name = topic_info['topic_input'].value
        if with_evaluation:
            output_header.append(topic_name + " (GroundTruth)")
        output_header.append(topic_name + " (Predicted)")
        output_header.append(topic_name + " (Probability)")

    with open(save_name + ".csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(output_header)

    # Assuming the first row of input CSV is header, actual data starts from index 1
    # If input CSV has no header, change start_row_index to 0
    start_row_index = 1 
    data_rows = reader_list[start_row_index:]
    total_rows = len(data_rows)
    processed_rows_count = 0
    current_batch_start_index_in_original_file = start_row_index 

    current_batch = []
    for original_row_index, row_content in enumerate(data_rows, start=start_row_index):
        current_batch.append(row_content)
        
        if len(current_batch) >= batch_size or (processed_rows_count + len(current_batch) == total_rows):
            # Process batch
            # Pass the extractor_instance to process_batch
            batch_results, batch_probs, batch_original_indices = process_batch(
                extractor_instance, 
                current_batch, 
                current_batch_start_index_in_original_file, # This is the original index from the file
                with_evaluation=with_evaluation, 
                constrained_output=constrained_output
            )
            
            # Write results and update metrics
            for i, (single_row_content, single_result_list, single_prob_list) in enumerate(zip(current_batch, batch_results, batch_probs)):
                original_file_row_id = batch_original_indices[i]
                
                # Update overall correct/relevant counts for evaluation report
                if with_evaluation:
                    for topic_idx, predicted_cat_name in enumerate(single_result_list):
                        # Ensure ground truth column exists for this topic
                        if (topic_idx + 1) < len(single_row_content):
                            ground_truth_cat_name = single_row_content[topic_idx + 1].strip()

                            if ground_truth_cat_name: # If there's a ground truth label
                                
                                eval_ground_truth = ground_truth_cat_name
                                eval_predicted = predicted_cat_name

                                # For Date Type Topics, we need to convert the ground truth date to the same format as the prediction
                                if extractor_instance.get_topics()[topic_idx]['topic_data'] == 'date':
                                    parsed_gt_date = dateparser.parse(ground_truth_cat_name, settings={'DATE_ORDER': 'DMY'})
                                    if parsed_gt_date:
                                        eval_ground_truth = parsed_gt_date.strftime('%Y-%m-%d')
                                    # If parsing fails, eval_ground_truth remains the original string.
                                    # The prediction is already in YYYY-MM-DD or None, so no change to eval_predicted

                                is_correct = eval_ground_truth == eval_predicted
                                num_relevant_attempts_per_topic[topic_idx] += 1
                                if is_correct:
                                    num_correct_results_per_topic[topic_idx] += 1

                                probability = single_prob_list[topic_idx]
                                per_topic_eval_data[topic_idx].append((probability, is_correct))
                
                process_and_write_result(
                    original_file_row_id, # Use original file row ID for output CSV
                    single_row_content, 
                    single_result_list, 
                    single_prob_list, 
                    save_name, 
                    with_evaluation, 
                    extractor_instance, # Pass instance for topic/category info
                    category_confusions # Pass dict to be updated
                )
            
            processed_rows_count += len(current_batch)
            print(f"Processed {processed_rows_count}/{total_rows} rows ({(processed_rows_count/total_rows)*100:.2f}%)")
            if progress_callback:
                progress_callback(processed_rows_count, total_rows)

            current_batch_start_index_in_original_file += len(current_batch)
            current_batch = [] # Clear batch

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Write evaluation metrics if with_evaluation is True
    if with_evaluation:
        with open(save_name + ".csv", 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow([]) # Empty row for spacing
            writer.writerow([
                "Topic", "Accuracy", "Correct Attempts", "Relevant Attempts",
                "Micro Acc (Recall)", "Micro Prec", "Micro F1",
                "TP Sum", "FP Sum", "FN Sum", "TN Sum" # Sums across all categories for the topic
            ])

            for i, topic_info_dict in enumerate(topics_data):
                topic_name = topic_info_dict['topic_input'].value
                
                accuracy_val = -1
                if num_relevant_attempts_per_topic[i] > 0:
                    accuracy_val = (num_correct_results_per_topic[i] / num_relevant_attempts_per_topic[i]) * 100.0
                
                # Check if it's a categorical topic to decide on detailed metrics
                if i in category_confusions:
                    sum_tp = 0
                    sum_fp = 0
                    sum_fn = 0
                    sum_tn = 0
                    for cat_name, conf_values in category_confusions[i].items():
                        sum_tp += conf_values["TP"]
                        sum_fp += conf_values["FP"]
                        sum_fn += conf_values["FN"]
                        sum_tn += conf_values["TN"]
                    
                    micro_recall_val = (sum_tp / (sum_tp + sum_fn)) if (sum_tp + sum_fn) > 0 else 0.0
                    micro_precision_val = (sum_tp / (sum_tp + sum_fp)) if (sum_tp + sum_fp) > 0 else 0.0
                    micro_f1_val = 2.0 * (micro_precision_val * micro_recall_val) / (micro_precision_val + micro_recall_val) if micro_precision_val > 0 and micro_recall_val > 0 else 0.0
                    
                    writer.writerow([
                        topic_name,
                        f"{accuracy_val:.2f}%" if accuracy_val != -1 else "N/A",
                        num_correct_results_per_topic[i],
                        num_relevant_attempts_per_topic[i],
                        f"{micro_recall_val*100:.2f}%",
                        f"{micro_precision_val*100:.2f}%",
                        f"{micro_f1_val*100:.2f}%",
                        sum_tp,
                        sum_fp,
                        sum_fn,
                        sum_tn
                    ])
                else:
                    # For non-categorical, write empty cells for detailed metrics
                    writer.writerow([
                        topic_name,
                        f"{accuracy_val:.2f}%" if accuracy_val != -1 else "N/A",
                        num_correct_results_per_topic[i],
                        num_relevant_attempts_per_topic[i],
                        "", "", "", "", "", "", "" # Empty cells for metrics
                    ])
            writer.writerow(["Elapsed Time", f"{elapsed_time:.2f} seconds"])

            print("\n--- Final Evaluation Report ---")
            total_correct = sum(num_correct_results_per_topic)
            total_relevant = sum(num_relevant_attempts_per_topic)
            
            # Detailed report per topic
            for i, topic_info in enumerate(extractor_instance.get_topics()):
                topic_name = topic_info['topic_input'].value
                accuracy = (num_correct_results_per_topic[i] / num_relevant_attempts_per_topic[i] * 100) if num_relevant_attempts_per_topic[i] > 0 else 0
                print(f"Topic: {topic_name} - Accuracy: {accuracy:.2f}% ({num_correct_results_per_topic[i]}/{num_relevant_attempts_per_topic[i]} correct)")
                # writer.writerow([
                #     topic_name,
                #     f"{accuracy:.2f}%" if accuracy != -1 else "N/A",
                #     num_correct_results_per_topic[i],
                #     num_relevant_attempts_per_topic[i],
                #     "", "", "", "", "", "", "" # Empty cells for metrics
                # ])
                # If it's a categorical topic, print confusion matrix details
                if i in category_confusions:
                    print(f"  Confusion Matrix for {topic_name}:")
                    # writer.writerow([
                    #     topic_name,
                    #     "", "", "", "", "", "", "", "", "", "" # Empty cells for metrics
                    # ])
                    for cat, values in category_confusions[i].items():
                        print(f"    Category: {cat} - TP: {values['TP']}, FP: {values['FP']}, FN: {values['FN']}")
                        # writer.writerow([
                        #     topic_name,
                        #     cat,
                        #     values['TP'],
                        #     values['FP'],
                        #     values['FN'],
                        #     "", "", "", "", "", "" # Empty cells for metrics
                        # ])

            # Overall accuracy
            overall_accuracy = (total_correct / total_relevant * 100) if total_relevant > 0 else 0
            print(f"\nOverall Accuracy: {overall_accuracy:.2f}% ({total_correct}/{total_relevant} correct)")
            writer.writerow([
                "", "", "", "", "", "", "", "", "", "", "" # Empty cells for metrics
            ])
            writer.writerow([
                "Overall Accuracy", f"{overall_accuracy:.2f}%" if overall_accuracy != -1 else "N/A",
                total_correct,
                total_relevant,
                "", "", "", "", "", "" # Empty cells for metrics
            ])
            writer.writerow([
                "", "", "", "", "", "", "", "", "", "", "" # Empty cells for metrics
            ])
            # High-confidence subsets accuracy
            print("\n--- Accuracy for High-Confidence Subsets ---")
            probability_thresholds = [0.90, 0.99, 0.999, 0.9999]

            for topic_idx, topic_info in enumerate(extractor_instance.get_topics()):
                topic_name = topic_info['topic_input'].value
                print(f"\nTopic: {topic_name}")
                writer.writerow([
                    topic_name,
                    "", "", "", "", "", "", "", "", "", "" # Empty cells for metrics
                ])
                for threshold in probability_thresholds:
                    confident_predictions = [item for item in per_topic_eval_data[topic_idx] if item[0] >= threshold]
                    count = len(confident_predictions)
                    if count > 0:
                        correct_confident = sum(1 for item in confident_predictions if item[1])
                        accuracy = (correct_confident / count) * 100
                    else:
                        accuracy = 0.0
                    
                    print(f"  - Accuracy at {threshold*100:.2f}% confidence ({count} items): {accuracy:.2f}%")
                    writer.writerow([
                        threshold*100,
                        f"{accuracy:.2f}%" if accuracy != -1 else "N/A",
                        correct_confident,
                        count,
                        "", "", "", "", "", "" # Empty cells for metrics
                    ])

    print(f"Classification of '{os.path.basename(dataset_path)}' complete. Output written to '{os.path.basename(save_name)}.csv'.")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

