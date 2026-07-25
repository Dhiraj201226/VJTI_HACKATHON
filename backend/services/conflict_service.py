from typing import List, Dict, Any
from models.schemas import Conflict

def detect_conflicts(retrieved_chunks: Dict[str, Any]) -> List[Conflict]:
    """
    Analyzes retrieved chunks for conflicting policy information.
    For this hackathon, we simulate detecting a conflict between the 2023 and 2024 AI Lab policies.
    """
    conflicts = []
    
    docs = retrieved_chunks.get('documents', [[]])[0]
    metadatas = retrieved_chunks.get('metadatas', [[]])[0]
    
    policy_areas = {}
    
    for i, meta in enumerate(metadatas):
        if not meta:
            continue
        area = meta.get('policy_area')
        if area:
            if area in policy_areas:
                # We found multiple documents for the same policy area. Potential conflict.
                old_doc = policy_areas[area]['doc']
                old_meta = policy_areas[area]['meta']
                new_doc = docs[i]
                new_meta = meta
                
                # Simple logic to determine older vs newer based on date string
                if new_meta.get('date', '') > old_meta.get('date', ''):
                    latest = new_meta
                    latest_doc = new_doc
                    older = old_meta
                    older_doc = old_doc
                else:
                    latest = old_meta
                    latest_doc = old_doc
                    older = new_meta
                    older_doc = new_doc
                
                conflict = Conflict(
                    conflict_id=f"conflict_{area.replace(' ', '_')}",
                    old_policy=f"GR {older.get('gr_number')}: {older_doc}",
                    latest_policy=f"GR {latest.get('gr_number')}: {latest_doc}",
                    reason="Conflicting budget limits and requirements found for the same policy area.",
                    recommendation=f"Recommend using the latest policy ({latest.get('gr_number')}) as it supersedes previous budget limits."
                )
                conflicts.append(conflict)
            else:
                policy_areas[area] = {'doc': docs[i], 'meta': meta}
                
    return conflicts
