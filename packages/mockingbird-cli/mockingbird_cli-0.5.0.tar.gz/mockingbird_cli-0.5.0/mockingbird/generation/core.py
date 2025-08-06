from typing import Dict, List, Any, Tuple, Optional

from rich.progress import Progress, TaskID
from mockingbird.common.exceptions import GeneratorError
from mockingbird.generation.execution_context import ExecutionContext
from mockingbird.generation.generators import Generator

class GenerationCore:
    def __init__(
        self,
        blueprint_data: Dict,
        execution_context: ExecutionContext,
        progress: Progress,
        task_id: TaskID,
        global_generator_configs: Optional[Dict] = None
    ):
        self.blueprint_data = blueprint_data
        self.global_generator_configs = global_generator_configs or {}
        self.execution_context = execution_context
        self.progress = progress
        self.task_id = task_id
        self.registry = self.execution_context.get_generator_registry()
        self._stateful_generator_instances: Dict[Tuple[str, str, str], Generator] = {}
        self._generator_instances_cache: Dict[Tuple[str, str, str], Generator] = {}

    def generate_data(self, sorted_entities: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        generated_data_store: Dict[str, List[Dict[str, Any]]] = {}
        self.execution_context.set_generated_data_store(generated_data_store)

        for entity_name in sorted_entities:
            entity_definition = self.blueprint_data.get(entity_name, {})
            count = entity_definition.get("count", 1)
            fields = entity_definition.get("fields", {})

            task_description = f"Generating {count} records for {entity_name}"
            self.progress.update(self.task_id, description=task_description)

            entity_task = self.progress.add_task(f"  - {entity_name}", total=count, indent=2)

            generated_data_store[entity_name] = []

            for i in range(count):
                current_row: Dict[str, Any] = {}
                for field_name, generator_config_value in fields.items():
                    try:
                        if not isinstance(generator_config_value, dict) or 'generator' not in generator_config_value or 'config' not in generator_config_value:
                            raise ValueError(
                                f"Field '{entity_name}.{field_name}' has an invalid configuration format. "
                                f"Expected {{'generator': 'type', 'config': {{...}}}}, but got: {generator_config_value}"
                            )
                        generator_name = generator_config_value['generator']
                        local_config = generator_config_value.get('config', {}) or {}

                        # Fetch global config for this generator type
                        global_config = self.global_generator_configs.get(generator_name, {})

                        # Merge configs: local overrides global
                        merged_config = {**global_config, **local_config}

                        generator_class = self.registry.get_generator_class(generator_name)
                        instance_key = (entity_name, field_name, generator_name)

                        if instance_key not in self._generator_instances_cache:
                            self._generator_instances_cache[instance_key] = generator_class(merged_config)

                        generator_instance = self._generator_instances_cache[instance_key]

                        current_row[field_name] = generator_instance.generate(
                            execution_context=self.execution_context,
                            current_row_data=current_row,
                            current_entity_name=entity_name,
                            current_row_index=i,
                            current_field_name=field_name
                        )
                    except GeneratorError as e:
                        # Catch the specific generator error for more detailed reporting
                        raise RuntimeError(
                            f"Error generating data for field '{entity_name}.{field_name}' (row {i+1}):\n"
                            f"{e}"
                        ) from e
                    except Exception as e:
                        # Catch any other unexpected errors during generation
                        raise RuntimeError(f"An unexpected error occurred while generating data for field '{entity_name}.{field_name}' (row {i+1}): {e}") from e

                generated_data_store[entity_name].append(current_row)
                self.progress.update(entity_task, advance=1)

            self.progress.update(self.task_id, advance=1)
            self.progress.update(entity_task, description=f"✅ {entity_name}")

        return generated_data_store
