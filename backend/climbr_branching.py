
from transformers import AutoModelForCausalLM
from hf_ehr.data.tokenization import CLMBRTokenizer
from hf_ehr.config import Event
from typing import List, Dict, Optional, Tuple
import torch
import copy
from apark_timeline import patient2
from mbishop_timeline import patient1
def run_branching_simulation():
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained("YaHi/gpt_clmbr")
    tokenizer = CLMBRTokenizer.from_pretrained("YaHi/gpt_clmbr")
    # Initial patient history
    initial_patient = patient2

    class ClinicalPath:
        """Represents a single diagnostic pathway"""
        def __init__(self, events: List[Event], path_id: str, parent_id: str = None):
            self.events = copy.deepcopy(events)
            self.path_id = path_id
            self.parent_id = parent_id
            self.diagnosis_found = False
            self.final_diagnosis = None
            self.steps = []  # Track the journey from initial patient state
            
        def add_event(self, token_text: str, probability: float):
            """Add a new event to this path"""
            # Parse the token to create an Event
            if '/' in token_text:
                system, code = token_text.split('/', 1)
                
                # Determine the table based on the system
                if system == 'LOINC':
                    omop_table = 'measurement'
                elif system == 'RxNorm':
                    omop_table = 'drug_exposure'
                elif system == 'SNOMED':
                    # Could be condition or observation
                    omop_table = 'condition_occurrence' if 'condition' in token_text.lower() else 'observation'
                elif system == 'CPT4':
                    omop_table = 'procedure_occurrence'
                else:
                    omop_table = 'observation'
                
                new_event = Event(
                    code=token_text,
                    value=f"Predicted: {token_text}",
                    unit=None,
                    start='2025-08-23T14:00:00.000Z',
                    end=None,
                    omop_table=omop_table
                )
                
                self.events.append(new_event)
                self.steps.append({
                    'token': token_text,
                    'probability': probability,
                    'type': omop_table
                })
                
                # Check if this is a diagnosis (condition_occurrence)
                if omop_table == 'condition_occurrence':
                    self.diagnosis_found = True
                    self.final_diagnosis = token_text

    def get_next_tokens(patient_events: List[Event], model, tokenizer, n_tokens: int = 2) -> List[Tuple[str, float]]:
        """Get top n predictions for next token given patient history"""
        batch = tokenizer([patient_events], add_special_tokens=True, return_tensors='pt')
        
        with torch.no_grad():
            outputs = model(**batch)
            logits = outputs.logits
        
        next_token_logits = logits[0, -1, :]
        next_token_probs = torch.softmax(next_token_logits, dim=-1)
        
        # Get top candidates to find meaningful tokens
        top_k = 100
        top_probs, top_indices = torch.topk(next_token_probs, min(top_k, len(next_token_probs)))
        
        predictions = []
        for i in range(len(top_indices)):
            token_id = top_indices[i].item()
            probability = top_probs[i].item()
            
            try:
                if hasattr(tokenizer, 'decode'):
                    token_text = tokenizer.decode([token_id])
                elif hasattr(tokenizer, 'convert_ids_to_tokens'):
                    token_text = tokenizer.convert_ids_to_tokens([token_id])[0]
                else:
                    continue
                
                # Skip special tokens and domain markers
                if (token_text == "Domain/OMOP generated" or 
                    token_text.startswith("Domain/") or 
                    token_text.startswith("Visit/") or
                    token_text in ['<pad>', '<unk>', '<s>', '</s>']):
                    continue
                
                # Only include medical codes with proper format
                if '/' in token_text and any(token_text.startswith(prefix) for prefix in ['LOINC/', 'SNOMED/', 'RxNorm/', 'CPT4/']):
                    # Check if this token already exists in the patient events
                    already_exists = any(event.code == token_text[:len(event.code)] for event in patient_events)
                    if not already_exists:
                        predictions.append((token_text, probability))
                        if len(predictions) >= n_tokens:
                            break
                            
            except Exception as e:
                continue
        
        return predictions

    # Start with a single root path
    root_path = ClinicalPath(initial_patient, "Path-0")
    current_paths = [root_path]

    # Perform 4 levels of branching (1 → 2 → 4 → 8 → 16)
    for level in range(4):
        next_paths = []
        
        for path_idx, path in enumerate(current_paths):
            # Skip if diagnosis already found or sequence limit reached
            if path.diagnosis_found:
                next_paths.append(path)  # Keep the path but don't branch
                continue
            
            # Get top 2 predictions for branching
            predictions = get_next_tokens(path.events, model, tokenizer, n_tokens=2)
            
            if len(predictions) == 0:
                next_paths.append(path)  # Keep the path but don't branch
                continue
            elif len(predictions) == 1:
                # Only one valid prediction, create one child
                child_path = ClinicalPath(path.events, f"Path-{level+1}-{path_idx*2}", parent_id=path.path_id)
                child_path.steps = copy.deepcopy(path.steps)  # Inherit parent's steps
                child_path.add_event(predictions[0][0], predictions[0][1])
                next_paths.append(child_path)
                print(f"{path.path_id} → {child_path.path_id}: {predictions[0][0]} (prob: {predictions[0][1]:.4f})")
            else:
                # Create two children paths
                for i, (token, prob) in enumerate(predictions[:2]):
                    child_path = ClinicalPath(path.events, f"Path-{level+1}-{path_idx*2+i}", parent_id=path.path_id)
                    child_path.steps = copy.deepcopy(path.steps)  # Inherit parent's steps
                    child_path.add_event(token, prob)
                    next_paths.append(child_path)
        
        current_paths = next_paths
    return current_paths, initial_patient
    