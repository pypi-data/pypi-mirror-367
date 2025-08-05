from dataclasses import dataclass
import json

import tiktoken


@dataclass
class ModelCosts:
    input_cost_per_million: float
    output_cost_per_million: float
    encoding_name: str

# 4th August 2025
MODEL_COSTS = {
    'gpt-4o-mini': ModelCosts(0.075, 0.300, 'o200k_base'),
    'gpt-4o': ModelCosts(1.25, 5, 'o200k_base'),
    'o3': ModelCosts(1, 4, 'o200k_base'),
    'o3-mini': ModelCosts(0.55, 2.2, 'o200k_base'),
    'o4-mini': ModelCosts(0.55, 2.2, 'o200k_base')
}

class Costs:
    def __init__(self, model):
        if model not in MODEL_COSTS.keys():
            raise ValueError(f"Model {model} not supported")

        self.model = model
        self.encoding_name = MODEL_COSTS[model].encoding_name

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(self.encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def input_tokens(self, filename):
        total_tokens = 0

        with open(filename) as f:
            for line in f.readlines():
                data = json.loads(line)
                for message in data['body']['input']:
                    total_tokens += self.num_tokens_from_string(message['content'])

        return total_tokens

    def input_cost(self, filename):
        return self.input_tokens(filename) * MODEL_COSTS[self.model].input_cost_per_million / 1_000_000

    def output_tokens(self, filename):
        total_tokens = 0

        with open(filename) as f:
            for line in f.readlines():
                data = json.loads(line)
                total_tokens += self.num_tokens_from_string(data['response']['body']['output'][0]['content'][0]['text'])

        return total_tokens

    def output_cost(self, filename):
        return self.output_tokens(filename) * MODEL_COSTS[self.model].output_cost_per_million / 1_000_000
