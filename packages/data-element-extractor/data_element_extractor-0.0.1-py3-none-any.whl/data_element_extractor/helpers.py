import torch
from transformers import StoppingCriteriaList, StoppingCriteria

class MockText:
    def __init__(self, value: str):
        self.value = value



class StopOnTokens(StoppingCriteria):
    def __init__(self, stop_token_ids):
        self.stop_token_ids = stop_token_ids

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        for stop_id in self.stop_token_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False




def serialize_topics(topics):
    data = []
    for topic_info in topics:
        topic_data = {
            'id': topic_info.get('id', ''),
            'topic_input': topic_info['topic_input'].value if 'topic_input' in topic_info else '',
                'topic_data': topic_info['topic_data'] if 'topic_data' in topic_info else '',
                'condition': topic_info['condition'].value if 'condition' in topic_info else '', # Topic-level condition
                'prompt': topic_info['prompt'].value if 'prompt' in topic_info else '',
                'thinking_config': topic_info.get('thinking_config', {}),
                'categories': []
        }
        # for entry in topic_info.get('categories', []):
        #     print(entry)
        #     print("Name")
        #     print(entry[0].value)
        #     print("Condition")
        #     print(entry[1].value)
        #     print("ID")
        #     print(entry[2].value)
        # print(topic_info.get('categories', [])[0].value)
        # print("Name")
        # print(topic_info.get('categories', [])[0].value)
        # print("Condition")
        # print(topic_info.get('categories', [])[1].value)
        # print("ID")
        # print(topic_info.get('categories', [])[2])
        # print("ooo")
        # Categories are (MockText(name), MockText(condition), cat_id)
        for (cat_name_mock, cat_id) in topic_info.get('categories', []):
            cat_name = cat_name_mock.value
            topic_data['categories'].append({
                'id': cat_id,
                    'name': cat_name,       # Using 'name' key
                })

        print(topic_data)
        data.append(topic_data)
    return data



def generate_symbols(symbol_config, num_items):
    if symbol_config == "alphabetical":
        return [chr(ord('A') + i) for i in range(num_items)]
    elif symbol_config == "numerical":
        return [str(i + 1) for i in range(num_items)]
    elif symbol_config and symbol_config != "none":
        symbols = [s.strip() for s in symbol_config.split(',')]
        if len(symbols) >= num_items:
            return symbols[:num_items]
    return None