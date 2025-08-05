import torch
from transformers import LogitsProcessor


default_grammar_words = [' the', ' to', ' and', ' of', ' a', ' in', ' that', ' you', ' it', ' for', ' on', ' he', ' with', ' this', ' as', ' we', ' but', ' at', ' they', ' what', ' his', ' from', ' by', ' or', ' she', ' my', ' all', ' an', ' her', ' about', ' me', ' if', ' your', ' can', ' who', ' out', ' their', ' like', ' would', ' when', ' him', ' them', ' some', ' how', ' which', ' than', ' our', ' into', ' because', ' these', ' over', ' us', ' its', ' where', ' after', ' any', ' those', ' should', ' may', ' through', ' why', ' before', ' off', ' while', ' around', ' another', ' both', ' between', ' every', ' each', ' might', ' since', ' against', ' without', ' must', ' during', ' under', ' though', ' until', ' whether', ' among', ' along', ' within', ' across', ' behind', ' either', ' himself', ' although', ' outside', ' themselves', ' is', ' was', ' be', ' have', ' are', ' do', ' had', ' has', ' were', ' will', ' did', ' been', ' could', ' does', ' need', ' being', ' am', ' used', ' doing', ' having']


class TokenSwapProcessor(LogitsProcessor):
    """
    This is a logit processor which implements tokenswap
    """
    
    def __init__(self, aux_model, tokenizer, grammar_words = None):
        """
        Initialize TokenSwap processor.
        
        Args:
            aux_model: Auxiliary model
            grammar_words: List of grammar words to apply swapping to
            tokenizer: Tokenizer
        """
        self.aux_model = aux_model
        self.tokenizer = tokenizer
        self.aux_past_kv = None
        self.first_call = True

        if grammar_words is None:
            grammar_words = default_grammar_words
        self.grammar_ids = torch.tensor([
            tokenizer.encode(word, add_special_tokens=False)[0] 
            for word in grammar_words
        ])
        
        device = next(aux_model.parameters()).device
        self.grammar_ids = self.grammar_ids.to(device)
        
    def __call__(self, input_ids, scores):

        with torch.no_grad():
            if self.first_call:
                aux_outputs = self.aux_model(input_ids, use_cache=True)
                self.first_call = False
            else:
                aux_outputs = self.aux_model(
                    input_ids[:, -1:], 
                    past_key_values=self.aux_past_kv, 
                    use_cache=True
                )
            
            self.aux_past_kv = aux_outputs.past_key_values
            
            p_main = torch.softmax(scores, dim=-1)
            p_aux = torch.softmax(aux_outputs.logits[:, -1], dim=-1)
            
            p_main_sum = p_main[:, self.grammar_ids].sum(dim=-1, keepdim=True)
            p_aux_sum = p_aux[:, self.grammar_ids].sum(dim=-1, keepdim=True)
            
            p_gen = p_main.clone()
            mask = p_aux_sum > 0
            if mask.any():
                ratio = p_main_sum / p_aux_sum.clamp(min=1e-10)
                p_gen[:, self.grammar_ids] = ratio * p_aux[:, self.grammar_ids]
                p_gen = p_gen / p_gen.sum(dim=-1, keepdim=True)
            
            return torch.log(p_gen.clamp(min=1e-10))