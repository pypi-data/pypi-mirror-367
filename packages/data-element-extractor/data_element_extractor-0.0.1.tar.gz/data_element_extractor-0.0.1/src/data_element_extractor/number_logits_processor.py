from transformers import LogitsProcessor
import torch


class NumberLogitsProcessor(LogitsProcessor):
    """
    A LogitsProcessor that constrains the output to be a valid number and then stops.
    It allows digits, at most one period, and a trailing space to signal completion.
    """
    def __init__(self, tokenizer, prompt_input_ids):
        self.tokenizer = tokenizer
        self.prompt_len = prompt_input_ids.input_ids.shape[1]
        allowed_tokens = [str(i) for i in range(10)] + ['.', ' ']
        
        self.allowed_token_ids = [tid for tid in self.tokenizer.convert_tokens_to_ids(allowed_tokens) if tid is not None]
        
        period_token = self.tokenizer.convert_tokens_to_ids('.')
        self.period_token_id = period_token[0] if isinstance(period_token, list) and len(period_token) > 0 else period_token

        space_token = self.tokenizer.convert_tokens_to_ids(' ')
        self.space_token_id = space_token[0] if isinstance(space_token, list) and len(space_token) > 0 else space_token

        if self.tokenizer.eos_token_id is not None:
            self.allowed_token_ids.append(self.tokenizer.eos_token_id)

    def __call__(self, input_ids, scores):
        generated_ids = input_ids[:, self.prompt_len:]

        for i, seq_generated_ids in enumerate(generated_ids):
            # If a space is generated, force EOS to stop generation.
            if self.space_token_id and self.space_token_id in seq_generated_ids:
                mask = torch.ones(scores.shape[1], dtype=torch.bool, device=scores.device)
                if self.tokenizer.eos_token_id is not None:
                    mask[self.tokenizer.eos_token_id] = False
                scores[i, mask] = -float('inf')
                continue

            current_allowed_token_ids = self.allowed_token_ids[:]

            # If a period is already in the generated part, remove it from allowed tokens
            if self.period_token_id in seq_generated_ids:
                if self.period_token_id in current_allowed_token_ids:
                    current_allowed_token_ids.remove(self.period_token_id)
            
            # A number cannot start with a period.
            if len(seq_generated_ids) == 0:
                 if self.period_token_id in current_allowed_token_ids:
                    current_allowed_token_ids.remove(self.period_token_id)

            mask = torch.ones(scores.shape[1], dtype=torch.bool, device=scores.device)
            valid_ids = [tid for tid in current_allowed_token_ids if 0 <= tid < scores.shape[1]]
            mask[valid_ids] = False
            scores[i, mask] = -float('inf')

        return scores
