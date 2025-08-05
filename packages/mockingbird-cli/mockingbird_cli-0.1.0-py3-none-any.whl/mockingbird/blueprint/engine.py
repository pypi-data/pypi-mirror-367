from pathlib import Path
import yaml # PyYAML

from pathlib import Path
import yaml

from ..common.exceptions import BlueprintValidationError
from ..generation.generators import GeneratorRegistry # Assuming GeneratorRegistry is accessible here

# Add this new function at the module level
def unknown_tag_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        value = node.value
        if tag_suffix == "faker":
            return {'generator': 'faker', 'config': {'generator': value}}
        elif tag_suffix == "sequence":
            start_at = 1
            if value:
                try:
                    start_at = int(value)
                except ValueError:
                    raise yaml.YAMLError(f"Invalid start value for !sequence: {value}")
            return {'generator': 'sequence', 'config': {'start_at': start_at}}
        elif tag_suffix == "ref":
            return {'generator': 'ref', 'config': {'ref': value}}
        elif tag_suffix == "expr":
            return {'generator': 'expr', 'config': {'expression': value}}
        elif tag_suffix == "llm":
            return {'generator': 'llm', 'config': {'prompt_template': value}}
        # For other unknown scalar tags, pass them through as strings.
        else:
            if value:
                return f"!{tag_suffix} {value}"
            else:
                return f"!{tag_suffix}"
    elif isinstance(node, yaml.MappingNode):
        data = loader.construct_mapping(node, deep=True)
        # For known tags that are expected to be mappings (like choice, timestamp)
        # or any other tag used with a mapping.
        # This makes the assumption that if a tag is on a mapping,
        # the mapping itself is the config.
        if tag_suffix in ["choice", "timestamp", "faker", "sequence", "ref", "expr", "llm"]:
             return {'generator': tag_suffix, 'config': data}
        # For other unknown mapping tags, retain original behavior or raise error.
        # Retaining original behavior for now:
        else:
            data["_tag_"] = tag_suffix
            return data
    elif isinstance(node, yaml.SequenceNode):
        # This case is less common for generator definitions.
        # Maintain original behavior: construct the sequence.
        # Depending on usage, this might need specific handling or be disallowed.
        return loader.construct_sequence(node)

    # Should not be reached for valid YAML and node types
    raise yaml.YAMLError(f"Unsupported YAML node type or structure for tag !{tag_suffix}")

class BlueprintEngine:
    def __init__(self):
        # Get the SafeLoader and add our multi-constructor for any tag starting with '!'
        self.yaml_loader = yaml.SafeLoader
        self.yaml_loader.add_multi_constructor('!', unknown_tag_constructor)
        self.generator_registry = GeneratorRegistry() # Initialize once

    def validate_blueprint_structure(self, blueprint_data: dict) -> None:
        """
        Validates the entire parsed blueprint structure, including generator configs.
        This should be called after parsing if full validation is needed.
        """
        if not isinstance(blueprint_data, dict):
            raise BlueprintValidationError(
                "The blueprint content must be a valid YAML structure mapping entity names to their configurations (a dictionary or map).\n"
                f"Found type: {type(blueprint_data).__name__} instead of a dictionary."
            )
        if not blueprint_data:
            raise BlueprintValidationError(
                "The blueprint is empty. Please define at least one entity and its fields."
            )

        # Separate entities and top-level settings
        entities = {k: v for k, v in blueprint_data.items() if k not in ['generators']}
        generators_config = blueprint_data.get('generators', {})

        # Validate top-level generator configurations if they exist
        if generators_config:
            if not isinstance(generators_config, dict):
                raise BlueprintValidationError("The 'generators' section must be a dictionary of generator configurations.")
            for gen_name, gen_config in generators_config.items():
                if not isinstance(gen_config, dict):
                    raise BlueprintValidationError(f"The configuration for generator '{gen_name}' under 'generators' must be a dictionary.")
                # Further validation could be done here if needed, e.g., against a known schema for each generator's global config.

        for entity_name, entity_config in entities.items():
            if not isinstance(entity_config, dict):
                raise BlueprintValidationError(
                    f"In your blueprint, the configuration for entity '{entity_name}' must be a dictionary (key-value pairs).\n"
                    f"Found type: {type(entity_config).__name__} for '{entity_name}'."
                )

            if 'fields' not in entity_config: # Check presence before type
                raise BlueprintValidationError(
                    f"Entity '{entity_name}' is missing a 'fields' section, which is required to define its data structure.\n"
                    f"Example:\n{entity_name}:\n  fields:\n    my_field: !sequence"
                )
            if not isinstance(entity_config['fields'], dict):
                 raise BlueprintValidationError(
                    f"In entity '{entity_name}', the 'fields' section must be a dictionary mapping field names to their generator configurations.\n"
                    f"Found type: {type(entity_config['fields']).__name__} for 'fields'."
                )

            if not entity_config['fields']: # Check after ensuring it's a dict
                 raise BlueprintValidationError(
                    f"Entity '{entity_name}' has an empty 'fields' section. Please define at least one field for this entity."
                )

            # Validate 'count' or 'max_count'
            count_present = 'count' in entity_config
            max_count_present = 'max_count' in entity_config

            if count_present and max_count_present:
                raise BlueprintValidationError(
                    f"In entity '{entity_name}', both 'count' and 'max_count' are defined. "
                    f"Please use only one of these settings to specify the number of records to generate."
                )

            # It's generally expected that an entity has a count if it has fields to generate.
            # However, an entity might exist solely to be referenced, or import data.
            # For now, we don't enforce count/max_count presence if fields are defined,
            # as the generation core might handle this (e.g. default to 0 or 1, or error if ambiguous).
            # This validation focuses on the type if present.

            if count_present:
                count_val = entity_config['count']
                if not isinstance(count_val, int) or count_val < 0:
                    raise BlueprintValidationError(
                        f"In entity '{entity_name}', the 'count' setting must be a non-negative integer (e.g., 0, 10, 100).\n"
                        f"Found: '{count_val}' (type: {type(count_val).__name__})."
                    )

            if max_count_present:
                max_count_val = entity_config['max_count']
                if not isinstance(max_count_val, int) or max_count_val < 0:
                    raise BlueprintValidationError(
                        f"In entity '{entity_name}', the 'max_count' setting must be a non-negative integer (e.g., 0, 10, 100).\n"
                        f"Found: '{max_count_val}' (type: {type(max_count_val).__name__})."
                    )

            for field_name, field_value in entity_config['fields'].items():
                is_generator_config_shape = isinstance(field_value, dict) and \
                                            'generator' in field_value and \
                                            'config' in field_value

                if is_generator_config_shape:
                    generator_name = field_value['generator']
                    generator_config = field_value.get('config', {})

                    if not isinstance(generator_config, dict):
                        raise BlueprintValidationError(
                            f"In entity '{entity_name}', field '{field_name}': The 'config' for generator '{generator_name}' is invalid.\n"
                            f"It must be a dictionary (a set of key-value pairs). Found type: {type(generator_config).__name__}."
                        )

                    try:
                        generator_class = self.generator_registry.get_generator_class(generator_name)
                    except ValueError as e:
                        available_generators = list(self.generator_registry._generators.keys())
                        available_generators_str = ", ".join(sorted(available_generators))
                        error_message = (
                            f"In entity '{entity_name}', field '{field_name}': Unknown generator '{generator_name}'.\n"
                            f"Please use one of the registered generator names. "
                            f"Available generators are: {available_generators_str}."
                        )
                        raise BlueprintValidationError(error_message) from e

                    try:
                        generator_class.validate_config(generator_config, blueprint_data, entity_name, field_name)
                    except BlueprintValidationError:
                        raise
                    except Exception as e:
                        # This catches unexpected errors within a generator's validate_config
                        raise BlueprintValidationError(
                            f"In entity '{entity_name}', field '{field_name}': An unexpected issue occurred while validating the configuration for generator '{generator_name}'.\n"
                            f"Details: {e}"
                        )
                else:
                    # Static value: string, number, boolean, list, or a plain dictionary not matching generator structure.
                    # No further validation for static values here; they are accepted as parsed.
                    pass


                # OLD LOGIC - keeping for reference during transition if needed.
                # if not isinstance(field_value, dict) or 'generator' not in field_value:
                #     if isinstance(field_value, (str, int, float, bool, list, type(None))): # Added dict and type(None) here
                #         continue # Static value
                #     # This condition might need adjustment if plain dicts are static values
                #     elif not isinstance(field_value, dict) or 'generator' not in field_value or 'config' not in field_value :
                #          raise BlueprintValidationError(
                #             f"Field '{entity_name}.{field_name}': Invalid configuration. "
                #             f"Expected a generator definition (e.g., !faker, or a map with 'generator' and 'config' keys) or a static value. Got: {field_value}"
                #         )


                # generator_name = field_value['generator']
                # generator_config = field_value.get('config', {})

                # if not isinstance(generator_config, dict):
                    raise BlueprintValidationError(
                        f"Field '{entity_name}.{field_name}': Generator config for '{generator_name}' must be a dictionary. Got: {generator_config}"
                    )

                try:
                    generator_class = self.generator_registry.get_generator_class(generator_name)
                except ValueError as e: # Raised by get_generator_class if name is not registered
                    raise BlueprintValidationError(f"Field '{entity_name}.{field_name}': {e}")

                try:
                    # Pass the original blueprint_data for potential cross-references
                    generator_class.validate_config(generator_config, blueprint_data, entity_name, field_name)
                except BlueprintValidationError:
                    raise # Re-raise to be caught by the caller
                except Exception as e: # Catch unexpected errors from validate_config
                    raise BlueprintValidationError(
                        f"Field '{entity_name}.{field_name}': Unexpected error during validation for generator '{generator_name}': {e}"
                    )


    def parse_blueprint(self, file_path: Path) -> dict:
        """
        Parses the Blueprint.yaml file.
        Custom tags like !faker will be loaded as strings by the unknown_tag_constructor.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Blueprint file not found: {file_path}")
        with open(file_path, 'r') as f:
            try:
                # Use the modified loader here
                data = yaml.load(f, Loader=self.yaml_loader)
                # self._validate_parsed_blueprint(data) # REMOVED: Validation is now separate
                if not isinstance(data, dict): # Basic check after load
                    raise BlueprintValidationError("Blueprint content must be a YAML dictionary.")
                return data
            except yaml.YAMLError as e:
                # Catch PyYAML specific errors
                raise BlueprintValidationError(f"Error parsing Blueprint YAML: {e}")
            # No longer need to catch BlueprintValidationError here from _validate_parsed_blueprint
            except Exception as e:
                # Catch other potential errors during loading
                raise BlueprintValidationError(f"An unexpected error occurred during blueprint parsing: {e}")

    def parse_blueprint_string(self, blueprint_string: str) -> dict:
        """
        Parses a blueprint string.
        Custom tags like !faker will be loaded as strings/mappings by the unknown_tag_constructor.
        """
        try:
            # Use the modified loader here
            data = yaml.load(blueprint_string, Loader=self.yaml_loader)
            # self._validate_parsed_blueprint(data) # REMOVED: Validation is now separate
            if not isinstance(data, dict): # Basic check after load
                raise BlueprintValidationError("Blueprint string content must be a YAML dictionary.")
            return data
        except yaml.YAMLError as e:
            # Catch PyYAML specific errors
            raise BlueprintValidationError(f"Error parsing Blueprint YAML string: {e}")
            # No longer need to catch BlueprintValidationError here
        except Exception as e:
            # Catch other potential errors
            raise BlueprintValidationError(f"An unexpected error occurred during blueprint string parsing: {e}")

    def generate_template_blueprint(self, template_name: str = "basic") -> str:
        # This method remains the same
        if template_name == "basic":
            return """
# Mockingbird Blueprint v1.0 - E-commerce Store Example
# This example blueprint generates mock data for a fictional e-commerce store,
# demonstrating various generators and their capabilities.

Customers:
  count: 50  # Generate 50 customers
  fields:
    customer_id: {generator: sequence, config: {start_at: 1}}
    first_name: {generator: faker, config: {generator: first_name}}
    last_name: {generator: faker, config: {generator: last_name}}
    email: {generator: faker, config: {generator: email}}
    street_address: {generator: faker, config: {generator: street_address}}
    city: {generator: faker, config: {generator: city}}
    state: {generator: faker, config: {generator: state_abbr}} # Using state abbreviation
    zip_code: {generator: faker, config: {generator: zipcode}}
    registration_date: {generator: timestamp, config: {start_date: "2010-01-01T00:00:00", end_date: "2023-12-31T23:59:59", format: "%Y-%m-%d"}}

Categories:
  count: 5  # Generate 5 product categories
  fields:
    category_id: {generator: sequence, config: {start_at: 101}} # Start at a different sequence
    category_name: {generator: enum, config: {values: ["Electronics", "Books", "Clothing", "Home & Kitchen", "Sports & Outdoors"]}}

Products:
  count: 100 # Generate 100 products
  fields:
    product_id: {generator: sequence, config: {start_at: 201}} # Start at a different sequence
    product_name: {generator: faker, config: {generator: catch_phrase}}
    description: {generator: faker, config: {generator: sentence, nb_words: 10}} # Longer description
    price: {generator: faker, config: {generator: pydecimal, left_digits: 4, right_digits: 2, positive: true, min_value: 5.00, max_value: 2000.00}}
    category_id: {generator: ref, config: {ref: Categories.category_id}}
    stock_quantity: {generator: faker, config: {generator: random_int, min: 0, max: 100}}
    added_date: {generator: faker, config: {generator: date_this_year}}

Orders:
  count: 75 # Generate 75 orders
  fields:
    order_id: {generator: sequence, config: {start_at: 301}} # Start at a different sequence
    customer_id: {generator: ref, config: {ref: Customers.customer_id}}
    order_date: {generator: faker, config: {generator: date_time_this_year}}
    status: {generator: choice, config: {choices: ["Pending", "Processing", "Shipped", "Delivered", "Cancelled", "Returned"], weights: [0.2, 0.2, 0.3, 0.2, 0.05, 0.05]}} # Added weights for status
    # total_amount should ideally be sum of order_items. For now, generate a plausible amount.
    # This assumes no direct aggregation feature in the generator for this field.
    total_amount: {generator: faker, config: {generator: pydecimal, left_digits: 8, right_digits: 2, positive: true, min_value: 10, max_value: 200000}}

OrderItems:
  count: 200 # Generate 200 order items
  fields:
    order_item_id: {generator: sequence, config: {start_at: 401}} # Start at a different sequence
    order_id: {generator: ref, config: {ref: Orders.order_id}}
    product_id: {generator: ref, config: {ref: Products.product_id}}
    quantity: {generator: faker, config: {generator: random_int, min: 1, max: 5}}
    # unit_price should be the price of the product (product_id) at the time of order.
    # Using the new RefGenerator feature to get 'price' from the record selected for 'product_id'.
    unit_price: {generator: ref, config: {use_record_from: product_id, field_to_get: price}}
    total_price: {generator: expr, config: {expression: "current['quantity'] * current['unit_price']"}}
"""
        else:
            return f"# Template '{template_name}' not found. Using basic template by default.\n" + self.generate_template_blueprint("basic")
