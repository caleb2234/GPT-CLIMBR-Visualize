from flask import Flask, jsonify
from flask_cors import CORS
import json
import subprocess
import sys
from pathlib import Path
from climbr_branching import run_branching_simulation

app = Flask(__name__)
CORS(app)

# Lazy load these large JSON files only when needed
loinc = None
cpt4 = None
cached_paths = None
cached_initial_patient = None

def load_code_mappings():
    """Lazy load LOINC and CPT4 mappings"""
    global loinc, cpt4
    if loinc is None:
        with open("loinc.json", "r") as f:
            loinc = json.load(f)
    if cpt4 is None:
        with open("cpt4.json", "r") as f:
            cpt4 = json.load(f)

@app.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint for k8s probes"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/pathways', methods=['GET'])
def get_pathways():
    """Run the CLMBR model and return the pathway results"""
    try:
        load_code_mappings()  # Load JSON files on first request

        # Parse the output to extract pathway data
        # This assumes you modify climbr_branching.py to output JSON at the end
        # Or you can parse the current_paths variable directly if imported
        
        # For now, we'll import and run the model directly

        
        # Convert the paths to JSON-serializable format
        pathways_data = []
        global cached_paths, cached_initial_patient
        if cached_paths is None:
            cached_paths, cached_initial_patient = run_branching_simulation()
        current_paths = cached_paths
        initial_patient = cached_initial_patient
        for path in current_paths:
            pathway = {
                'id': path.path_id,
                'parent_id': path.parent_id,
                'diagnosis_found': path.diagnosis_found,
                'final_diagnosis': path.final_diagnosis,
                'steps': []
            }
            
            for step in path.steps:
                # Parse the token to get system and code
                token = step['token']
                system = token.split('/')[0] if '/' in token else 'Unknown'
                code = token.split('/', 1)[1] if '/' in token else token
                code_only = code.split('/')[-1].split(" ")[0] if '/' in code else code
                display_name = code  # Default to showing the code
                if system == 'LOINC' and code_only in loinc:
                    if not loinc[code_only]["DisplayName"]:
                        display_name = loinc[code_only]["LONG_COMMON_NAME"]
                    else:
                        display_name = loinc[code_only]["DisplayName"]
                if system == 'CPT4' and code_only in cpt4:
                    display_name = cpt4[code_only]
                pathway['steps'].append({
                    'token': token,
                    'system': system,
                    'code': display_name,
                    'fullcode': code,
                    'probability': step['probability'],
                    'type': step['type']
                })
            
            pathways_data.append(pathway)
        
        # Get initial patient data
        initial_data = []
        for event in initial_patient:
            system = event.code.split('/')[0] if '/' in event.code else 'Unknown'
            code_only = event.code.split('/')[-1].split(" ")[0] if '/' in event.code else event.code
            display_name = event.code  # Default to showing the code
            if system == 'LOINC' and code_only in loinc:
                if not loinc[code_only]["DisplayName"]:
                    display_name = loinc[code_only]["LONG_COMMON_NAME"]
                else:
                    display_name = loinc[code_only]["DisplayName"]
            if system == 'CPT4' and code_only in cpt4:
                display_name = cpt4[code_only]
            initial_data.append({
                'code': event.code,
                'name': display_name,
                'system': system,
                'value': event.value,
                'omop_table': event.omop_table
            })
        
        return jsonify({
            'initial_patient': initial_data,
            'pathways': pathways_data,
            'total_paths': len(pathways_data),
            'paths_with_diagnosis': sum(1 for p in pathways_data if p['diagnosis_found'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """Get most frequent codes across all pathways"""
    try:
        load_code_mappings()  # Load JSON files on first request
        from collections import Counter
        
        # Use cached paths if available
        global cached_paths
        if cached_paths is None:
            cached_paths, _ = run_branching_simulation()
        current_paths = cached_paths
        
        # Track unique code positions to avoid double-counting
        # Key: (level, branch_index, step_number), Value: code
        unique_code_positions = {}
        
        # Process each path
        for path in current_paths:
            # Parse path ID to understand its position in the tree
            path_parts = path.path_id.split('-')
            if len(path_parts) >= 2:
                level = int(path_parts[1]) if path_parts[1].isdigit() else 4
                path_index = int(path_parts[2]) if len(path_parts) > 2 and path_parts[2].isdigit() else 0
            else:
                level = 4
                path_index = 0
            
            # Track codes by their position in the branching structure
            for step_idx, step in enumerate(path.steps):
                if step_idx == 0:
                    # First step - 8 paths share each code
                    position_key = (1, path_index // 8, 0)
                elif step_idx == 1:
                    # Second step - 4 paths share each code
                    position_key = (2, path_index // 4, 0)
                elif step_idx == 2:
                    # Third step - 2 paths share each code
                    position_key = (3, path_index // 2, 0)
                elif step_idx == 3:
                    # Fourth step - unique to each path
                    position_key = (4, path_index, 0)
                else:
                    # Any additional steps
                    position_key = (4, path_index, step_idx)
                
                # Store the code at this position
                unique_code_positions[position_key] = step['token']
        
        # Count unique codes
        code_counter = Counter(unique_code_positions.values())
        total_positions = len(unique_code_positions)
        
        # Convert to predictions format
        predictions = []
        for code, count in code_counter.most_common(10):
            percentage = (count / total_positions) * 100
            system = code.split('/')[0] if '/' in code else 'Unknown'
            code_only = code.split('/')[-1].split(" ")[0] if '/' in code else code
            display_name = code  # Default to showing the code
            if system == 'LOINC' and code_only in loinc:
                if not loinc[code_only]["DisplayName"]:
                    display_name = loinc[code_only]["LONG_COMMON_NAME"]
                else:
                    display_name = loinc[code_only]["DisplayName"]
            if system == 'CPT4' and code_only in cpt4:
                display_name = cpt4[code_only]
            predictions.append({
                'name': display_name,  # Truncate long codes
                'probability': round(percentage, 1),
                'code':code,
                'system': system,
                'count': count
            })
        
        return jsonify({'predictions': predictions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)