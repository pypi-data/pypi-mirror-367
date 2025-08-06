from typing import List, Dict, Set

def resolve_dependencies(entities: Dict[str, Dict]) -> List[str]:
    """
    Determines the correct order of entity generation based on !ref dependencies.
    Builds a Directed Acyclic Graph (DAG) and performs a topological sort.

    Args:
        entities: A dictionary where keys are entity names and values are their definitions
                  (parsed from Blueprint.yaml). The relevant part of the definition
                  is checking for fields that use the '!ref' tag.

    Returns:
        A list of entity names in the correct generation order.

    Raises:
        ValueError: If a circular dependency is detected or a referenced entity is not found.
    """
    if not entities:
        return []

    adj: Dict[str, Set[str]] = {name: set() for name in entities}
    in_degree: Dict[str, int] = {name: 0 for name in entities}
    entity_names = list(entities.keys())

    for entity_name, definition in entities.items():
        if 'fields' in definition and isinstance(definition['fields'], dict):
            for field_name, field_attrs in definition['fields'].items():
                if isinstance(field_attrs, str) and field_attrs.startswith("!ref "):
                    try:
                        referenced_entity = field_attrs.split(" ")[1].split(".")[0]
                        if referenced_entity not in entity_names:
                            raise ValueError(f"Entity '{entity_name}' field '{field_name}' references non-existent entity '{referenced_entity}'.")
                        if referenced_entity != entity_name: # Self-references are not graph edges for this purpose
                            adj[referenced_entity].add(entity_name)
                            in_degree[entity_name] +=1
                    except IndexError:
                        raise ValueError(f"Invalid !ref format in '{entity_name}.{field_name}': {field_attrs}")

    queue: List[str] = [name for name in entity_names if in_degree[name] == 0]
    sorted_list: List[str] = []

    while queue:
        current_entity = queue.pop(0)
        sorted_list.append(current_entity)

        for neighbor in sorted(list(adj[current_entity])): # Sort for deterministic output if multiple paths
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_list) != len(entity_names):
        # Identify problematic entities for better error message
        missing_entities = set(entity_names) - set(sorted_list)
        # A more sophisticated cycle detection algorithm could pinpoint the exact cycle.
        # For now, just list entities that couldn't be scheduled.
        raise ValueError(f"Circular dependency detected or missing entities. Could not resolve order for: {missing_entities}")

    return sorted_list
