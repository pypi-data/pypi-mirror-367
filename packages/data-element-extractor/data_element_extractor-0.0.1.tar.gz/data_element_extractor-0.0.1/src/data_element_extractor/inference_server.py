from flask import Flask, request, jsonify
import json
# from .models import ModelManager
from .extractor import DataElementExtractor

app = Flask(__name__)
extractor = DataElementExtractor()

class InferenceServer:
    def __init__(self):
        pass

    @staticmethod
    def start_server(host='127.0.0.1', port=5000, debug=False):
        """Start the Flask server explicitly."""
        print(f"Starting inference server on {host}:{port}")
        app.run(host=host, port=port, debug=debug)

    # Endpoint to set Inference Model
    @app.route('/set_model', methods=['POST'])
    def set_model():
        data = request.get_json()
        model_name = data.get('model_name')
        model_type = data.get('model_type')
        api_key = data.get('api_key')
        inference_type = "transformers"#data.get('inference_type')
        attn_implementation = data.get('attn_implementation')
        move_to_gpu = data.get('move_to_gpu')
        device_map = data.get('device_map')
        # model_manager = ModelManager()
        # model_manager.set_model(model_name, model_type, api_key, inference_type, attn_implementation, move_to_gpu, device_map)
        extractor.set_model(model_name, model_type, api_key, inference_type, attn_implementation, move_to_gpu, device_map)
        print("Model set successfully: ", model_name)
        print("Model type: ", model_type)
        print("API key: ", api_key)
        print("Inference type: ", inference_type)
        print("Attention implementation: ", attn_implementation)
        print("Move to GPU: ", move_to_gpu)
        print("Device map: ", device_map)
        return jsonify({'received_data': data})

    # Endpoint to Update Topics
    @app.route('/update_topics', methods=['POST'])
    def update_topics():
        data = request.get_json()
        topics = data.get('topics')
        extractor.update_topics(topics)
        print("Topics updated successfully: ", topics)
        return jsonify({'received_data': data})

    # Endpoint to get answer
    @app.route('/get_answer', methods=['POST'])
    def get_answer():
        data = request.get_json()
        prompt = data.get('prompt')
        categories = data.get('categories')
        constrained_output = data.get('constrained_output')
        temperature = data.get('temperature')
        thinking_data = data.get('thinking_data')
        # model_manager = ModelManager()
        answer, probability = extractor.model_manager.get_answer(prompt, categories, constrained_output, temperature, thinking_data)
        print("Answer: ", answer)
        return jsonify({'answer': answer, 'probability': probability})


    # Endpoint to get non categorical answer
    @app.route('/get_non_categorical_answer', methods=['POST'])
    def get_non_categorical_answer():
        data = request.get_json()
        prompt = data.get('prompt')
        # topic looks like this {'id': 'T2', 'topic_input': 'Maximum Speed', 'topic_data': 'number', 'condition': '', 'prompt': "INSTRUCTION: You are a helpful extractor. You select the correct number value for the topic. The topic of the extraction is '[TOPIC]'. QUESTION: The text for the extraction is '[TEXT]'. ANSWER: The correct number value for this text is '", 'thinking_config': {}, 'categories': []};
        # turn topic into .json
        topic = data.get('topic')
        constrained_output = data.get('constrained_output')
        temperature = data.get('temperature')
        thinking_data = data.get('thinking_data')
        print("Constrained output: ", constrained_output)
        # model_manager = ModelManager()
        answer, probability = extractor.model_manager.get_non_categorical_answer(prompt, topic, constrained_output, temperature, thinking_data)
        print("Answer: ", answer)
        print("Probability: ", probability)
        return jsonify({'answer': answer, 'probability': probability})



