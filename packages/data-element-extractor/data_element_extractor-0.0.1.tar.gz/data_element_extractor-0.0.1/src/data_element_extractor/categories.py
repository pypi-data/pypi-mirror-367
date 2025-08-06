import uuid
from .helpers import MockText


class CategoriesManager:
    def __init__(self):
        pass



    def add_category(self, topics,topicId, categoryName):
        topic_found = False
        for topic in topics:
            if topic.get('id') == topicId:
                category_id = str(uuid.uuid4())
                topic['categories'].append((MockText(categoryName), category_id))
                topic_found = True
                print(f"Category '{categoryName}' added to topic ID {topicId} with ID {category_id}.")
                return category_id
        if not topic_found:
            print(f"Topic with ID {topicId} not found.")


    def remove_category(self, topics, topic_to_remove_from, category_id_to_remove, inference_type="transformers"):
        # First, find the topic from which the category is being removed
        if not topic_to_remove_from:
            print(f"Topic with ID {topic_to_remove_from} not found.")
            return

        # Construct the reference string for the category to be removed
        # This assumes a condition format like 'topic_id==category_id'
        category_ref_str = f"{topic_to_remove_from['id']}=={category_id_to_remove}"

        # Iterate through all topics to find and remove referencing conditions
        for topic in topics:
            conditions = topic['condition'].value
            if conditions:
                conditions = conditions.split(' AND ')
                for condition in conditions:
                    if condition == category_ref_str:
                        topic['condition'].value = ""
                        print(f"Removed condition '{category_ref_str}' from topic ID {topic['id']}.")

        # Now, remove the actual category from its topic
        categories = topic_to_remove_from['categories']
        for i, (_, cat_id) in enumerate(categories):
            if cat_id == category_id_to_remove:
                del categories[i]
                print(f"Category with ID {category_id_to_remove} removed from topic ID {topic_to_remove_from['id']}.")
                return

        print(f"Category with ID {category_id_to_remove} not found in topic ID {topic_to_remove_from['id']}.")


            

  
    def add_category_condition(self, topics, topic_id, category_id, condition_str):
        """Adds or updates a condition for a specific category within a topic."""
        for topic in topics:
            if topic.get('id') == topic_id:
                for i, category_tuple in enumerate(topic['categories']):
                    # category_tuple is (name_mock, condition_mock, cat_id_in_topic)
                    if len(category_tuple) == 3 and category_tuple[2] == category_id:
                        condition_mock = category_tuple[1]
                        condition_mock.value = condition_str
                        print(f"Condition '{condition_str}' set for category ID {category_id} in topic ID {topic_id}.")
                        return
                print(f"Category ID {category_id} not found in topic ID {topic_id}.")
                return
        print(f"Topic ID {topic_id} not found.")



    def remove_category_condition(self, topics, topic_id, category_id):
        """Removes a condition from a specific category within a topic (sets it to empty string)."""
        for topic in topics:
            if topic.get('id') == topic_id:
                for i, category_tuple in enumerate(topic['categories']):
                    if len(category_tuple) == 3 and category_tuple[2] == category_id:
                        condition_mock = category_tuple[1]
                        condition_mock.value = ""
                        print(f"Condition removed from category ID {category_id} in topic ID {topic_id}.")
                        return
                print(f"Category ID {category_id} not found in topic ID {topic_id}.")
                return
        print(f"Topic ID {topic_id} not found.")


    def evaluate_condition(self, condition, previous_results):
        """
        Evaluate complex conditions with boolean operators.
        Supports conditions like:
        - "T1==cat1"
        - "T1==cat1 && T2==cat2"
        - "T1==cat1 || T2==cat2"
        - "(T1==cat1 && T2==cat2) || T3==cat3"
        - "T1!=cat1" (not equals)
        """
        if not condition or condition.strip() == "":
            return True

        condition = condition.strip()
        
        # Handle parentheses first
        if "(" in condition and ")" in condition:
            return self.evaluate_condition_with_parentheses(condition, previous_results)
        
        # Handle boolean operators
        if "&&" in condition:
            parts = [part.strip() for part in condition.split("&&")]
            return all(self.evaluate_single_condition(part, previous_results) for part in parts)
        elif "||" in condition:
            parts = [part.strip() for part in condition.split("||")]
            return any(self.evaluate_single_condition(part, previous_results) for part in parts)
        else:
            # Single condition
            return self.evaluate_single_condition(condition, previous_results)



    def evaluate_single_condition(self, condition, previous_results):
        """Evaluate a single condition like T1==cat1 or T1!=cat1"""
        condition = condition.strip()
        
        # Handle == operator
        if "!=" in condition:
            topic_id, expected_value = [x.strip() for x in condition.split("!=", 1)]
            operator = "!="
        elif "==" in condition:
            topic_id, expected_value = [x.strip() for x in condition.split("==", 1)]
            operator = "=="
        else:
            print(f"Invalid condition format: {condition}")
            return False

        if topic_id not in previous_results:
            return False

        actual_value = previous_results[topic_id]
        
        if operator == "==":
            return str(actual_value) == str(expected_value)
        elif operator == "!=":
            return str(actual_value) != str(expected_value)



    def evaluate_condition_with_parentheses(self, condition, previous_results):
        """Handle conditions with parentheses"""
        # Simple recursive evaluation for parentheses
        # This handles basic nested parentheses
        
        # Find innermost parentheses
        start = condition.rfind("(")
        if start == -1:
            return self.evaluate_condition(condition, previous_results)
            
        end = condition.find(")", start)
        if end == -1:
            print(f"Mismatched parentheses in condition: {condition}")
            return False
            
        # Evaluate the expression inside parentheses
        inner_condition = condition[start + 1:end]
        inner_result = self.evaluate_condition(inner_condition, previous_results)
        
        # Replace the parentheses with the result
        new_condition = condition[:start] + str(inner_result).lower() + condition[end + 1:]
        
        # Continue evaluating the new condition
        return self.evaluate_condition(new_condition, previous_results)


