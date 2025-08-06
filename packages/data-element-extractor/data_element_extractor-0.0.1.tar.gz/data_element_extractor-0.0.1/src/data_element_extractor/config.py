class Config:
    def __init__(self):
        self.server_url = "https://localhost:3000"
        # Options: "none", "alphabetical", "numerical", or a comma-separated list of custom symbols
        self.choice_symbol_config = "none"
        self.constrained_output_config = True
        self.inference_server_url = "http://127.0.0.1:5000"

    def get_server_url(self):
        return self.server_url

    def set_server_url(self, url):
        self.server_url = url

    def get_inference_server_url(self):
        return self.inference_server_url

    def set_inference_server_url(self, url):
        self.inference_server_url = url

    def get_choice_symbol_config(self):
        return self.choice_symbol_config

    def set_choice_symbol_config(self, value):
        self.choice_symbol_config = value

    def get_constrained_output_config(self):
        return self.constrained_output_config

    def set_constrained_output_config(self, value):
        self.constrained_output_config = value

config = Config()
