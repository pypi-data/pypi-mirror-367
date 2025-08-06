from abc import ABC, abstractmethod
import decimal
import math
from typing import Any, Dict, Optional, List, Type
from ..common.exceptions import BlueprintValidationError, GeneratorError
import uuid
from faker import Faker # Ensure Faker is imported
from faker.providers import company, automotive, bank, credit_card, job
import random # For ChoicesGenerator, and potentially for seeding Faker if needed directly
from asteval import Interpreter # Add this import
from dateutil import parser
from mockingbird.providers.commerce_provider import CommerceProvider

# Forward declaration for ExecutionContext type hint if not directly importable yet
# class ExecutionContext: pass # Not needed if we use 'Any' or import later

class Generator(ABC):
    @abstractmethod
    def generate(self, current_row_data: Optional[Dict[str, Any]] = None, execution_context: Optional[Any] = None) -> Any:
        pass

    @classmethod
    @abstractmethod
    def validate_config(cls, config: dict, all_blueprint_data: dict, current_entity_name: str, current_field_name: str) -> None:
        """
        Validates the configuration for this generator.
        Raises BlueprintValidationError if the config is invalid.

        :param config: The configuration dictionary for the specific generator instance.
        :param all_blueprint_data: The entire parsed blueprint data, for cross-reference validation (e.g., !ref).
        :param current_entity_name: The name of the entity this field belongs to.
        :param current_field_name: The name of the field this generator is for.
        """
        pass

class GeneratorRegistry:
    def __init__(self):
        self._generators: Dict[str, type[Generator]] = {} # Store generator classes
        self._register_default_generators()

    def register_generator(self, name: str, generator_class: type[Generator]):
        self._generators[name] = generator_class

    def get_generator_class(self, name: str) -> type[Generator]:
        generator_class = self._generators.get(name)
        if not generator_class:
            raise ValueError(f"Generator class '{name}' not registered.")
        return generator_class

    def _register_default_generators(self):
        self.register_generator("sequence", SequenceGenerator) # Example
        self.register_generator("faker", FakerGenerator)
        self.register_generator("choice", ChoicesGenerator)
        self.register_generator("ref", RefGenerator)
        self.register_generator("expr", ExprGenerator) # Ensure ExprGenerator is registered
        # self.register_generator("llm", LLMGenerator)   # Ensure LLMGenerator is registered if used
        self.register_generator("enum", EnumGenerator) # Register the new EnumGenerator
        self.register_generator("timestamp", TimestampGenerator )
        # ... other generators
        pass

# --- Generator Implementations ---
class SequenceGenerator(Generator):
    def __init__(self, config: dict):
        self.current_value = config.get('start_at', 1)
        self.increment = config.get('increment', 1)
    def generate(self, **kwargs) -> Any:
        value = self.current_value
        self.current_value += self.increment
        return value

    @classmethod
    def validate_config(cls, config: dict, all_blueprint_data: dict, current_entity_name: str, current_field_name: str) -> None:
        if 'start_at' in config:
            start_at_val = config['start_at']
            if not isinstance(start_at_val, int):
                raise BlueprintValidationError(
                    f"In entity '{current_entity_name}', field '{current_field_name}': "
                    f"SequenceGenerator setting 'start_at' must be an integer. Found: '{start_at_val}' (type: {type(start_at_val).__name__}).\n"
                    f"Example: start_at: 1"
                )

class FakerGenerator(Generator):
    # Class-level cache for Faker instances, keyed by (locale, seed)
    # typing.Tuple is used for compatibility if older Python versions are a concern, otherwise just tuple
    _faker_instances_cache: Dict[tuple[Optional[str], Optional[int]], Faker] = {}

    def __init__(self, config: dict):
        self.provider_expression = config.get('generator')
        if not self.provider_expression:
            raise ValueError("FakerGenerator config must include 'generator' key for provider expression.")
        self.locale = config.get('locale') # Optional, defaults to Faker's default locale if None
        self.faker_instance: Optional[Faker] = None # This will hold the instance for this generator object

        # Store additional arguments for the Faker provider
        self.provider_args: Dict[str, Any] = {
            key: value for key, value in config.items()
            if key not in ['generator', 'locale']
        }

    def _get_or_create_faker_instance(self, seed_value: Optional[int] = None) -> Faker:
        cache_key = (self.locale, seed_value)

        if cache_key in FakerGenerator._faker_instances_cache:
            return FakerGenerator._faker_instances_cache[cache_key]
        else:
            new_faker_instance = Faker(self.locale)
            new_faker_instance.add_provider(CommerceProvider)
            #providers=[FoodProvider, MusicProvider, CommerceProvider, AirTravelProvider])
            # print all provider names here
            if seed_value is not None:
                new_faker_instance.seed_instance(seed_value)
            
            FakerGenerator._faker_instances_cache[cache_key] = new_faker_instance
            return new_faker_instance

    def generate(self, execution_context: Optional[Any] = None, **kwargs) -> Any:
        current_seed: Optional[int] = None
        if execution_context and hasattr(execution_context, 'seed') and execution_context.seed is not None:
            current_seed = execution_context.seed

        # Ensure self.faker_instance is set for this call, using the cache
        self.faker_instance = self._get_or_create_faker_instance(current_seed)

        if self.faker_instance is None: # Should ideally not happen if _get_or_create_faker_instance works
            raise RuntimeError("Faker instance could not be initialized in FakerGenerator.")

        try:
            # Handle dotted expressions like "internet.email"
            provider_parts = self.provider_expression.split('.')
            target_provider = self.faker_instance
            for part in provider_parts:
                target_provider = getattr(target_provider, part)

            if callable(target_provider):
                return target_provider(**self.provider_args)
            else:
                # If the final attribute is not callable, it might be a property
                # In Faker, most data generators are methods.
                # This case might indicate an incorrect provider_expression.
                # For simplicity, we assume it's a method. If it could be a property,
                # this would need adjustment or clearer spec for provider_expression.
                raise AttributeError(f"Provider expression '{self.provider_expression}' resolved to a non-callable attribute on Faker instance.")

        except AttributeError:
            raise AttributeError(f"Invalid Faker provider expression: '{self.provider_expression}'")
        except Exception as e:
            # Catch other potential errors during Faker generation
            raise RuntimeError(f"Error generating fake data for '{self.provider_expression}': {e}")

    @classmethod
    def validate_config(cls, config: dict, all_blueprint_data: dict, current_entity_name: str, current_field_name: str) -> None:
        if 'generator' not in config:
            raise BlueprintValidationError(
                f"In entity '{current_entity_name}', field '{current_field_name}': "
                f"FakerGenerator is missing the required 'generator' setting, which specifies the Faker provider.\n"
                f"Example: generator: \"name\""
            )

        generator_val = config['generator']
        if not isinstance(generator_val, str):
            raise BlueprintValidationError(
                f"In entity '{current_entity_name}', field '{current_field_name}': "
                f"FakerGenerator setting 'generator' must be a string (the Faker provider name). Found: '{generator_val}' (type: {type(generator_val).__name__}).\n"
                f"Example: generator: \"internet.email\""
            )

        if 'locale' in config:
            locale_val = config['locale']
            if not isinstance(locale_val, str):
                raise BlueprintValidationError(
                    f"In entity '{current_entity_name}', field '{current_field_name}': "
                    f"FakerGenerator setting 'locale' must be a string if provided (e.g., \"en_US\"). Found: '{locale_val}' (type: {type(locale_val).__name__})."
                )

class ChoicesGenerator(Generator):
    def __init__(self, config: dict):
        self.choices = config.get('choices', [])
        if not self.choices:
            raise ValueError("ChoicesGenerator config must include 'choices' key.")
        self.weights = config.get('weights')
        if self.weights and len(self.choices) != len(self.weights):
            raise ValueError("Number of choices must match number of weights.")
    def generate(self, execution_context: Optional[Any] = None, **kwargs) -> Any:
        rand_instance = random # Default to global random

        if execution_context and hasattr(execution_context, 'get_seeded_random_instance'):
            rand_instance = execution_context.get_seeded_random_instance()
        # If execution_context is present but doesn't have get_seeded_random_instance (e.g. old mock),
        # it will fall back to global random, which might be seeded if EC's __init__ was called.

        if not self.choices:
            return None
        if self.weights:
            return rand_instance.choices(self.choices, weights=self.weights, k=1)[0]
        else:
            return rand_instance.choice(self.choices)

    @classmethod
    def validate_config(cls, config: dict, all_blueprint_data: dict, current_entity_name: str, current_field_name: str) -> None:
        if 'choices' not in config:
            raise BlueprintValidationError(
                f"In entity '{current_entity_name}', field '{current_field_name}': "
                f"ChoicesGenerator is missing the required 'choices' setting (a list of values).\n"
                f"Example: choices: [\"apple\", \"banana\", \"cherry\"]"
            )

        choices_val = config['choices']
        if not isinstance(choices_val, list) or not choices_val:
            raise BlueprintValidationError(
                f"In entity '{current_entity_name}', field '{current_field_name}': "
                f"ChoicesGenerator setting 'choices' must be a non-empty list. Found: '{choices_val}'.\n"
                f"Example: choices: [10, 20, 30]"
            )

        if 'weights' in config:
            weights_val = config['weights']
            if not isinstance(weights_val, list):
                raise BlueprintValidationError(
                    f"In entity '{current_entity_name}', field '{current_field_name}': "
                    f"ChoicesGenerator setting 'weights' must be a list of numbers if provided. Found: '{weights_val}' (type: {type(weights_val).__name__})."
                )
            if len(choices_val) != len(weights_val):
                raise BlueprintValidationError(
                    f"In entity '{current_entity_name}', field '{current_field_name}': "
                    f"ChoicesGenerator settings 'choices' (length {len(choices_val)}) and 'weights' (length {len(weights_val)}) must have the same number of elements."
                )
            if not all(isinstance(w, (int, float)) and w >= 0 for w in weights_val):
                raise BlueprintValidationError(
                    f"In entity '{current_entity_name}', field '{current_field_name}': "
                    f"ChoicesGenerator setting 'weights' must be a list of non-negative numbers. Found: {weights_val}."
                )

import datetime # Required for TimestampGenerator

class TimestampGenerator(Generator):
    def __init__(self, config: dict):
        self.start_date_str = config.get('start_date')
        if not self.start_date_str:
            raise ValueError("TimestampGenerator config must include 'start_date' key.")
        self.end_date_str = config.get('end_date')
        if not self.end_date_str:
            raise ValueError("TimestampGenerator config must include 'end_date' key.")
        self.format_string = config.get('format') # Optional format string

        try:
            # Attempt to parse dates at initialization to catch errors early
            # Common formats to try for parsing input dates
            self.start_date = self._parse_datetime_flexible(self.start_date_str)
            self.end_date = self._parse_datetime_flexible(self.end_date_str)
        except ValueError as e:
            raise ValueError(f"Invalid date string format: {e}")

        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date.")

    def _parse_datetime_flexible(self, date_string: str) -> datetime.datetime:
        """Tries to parse a date string using common date and datetime formats."""
        formats_to_try = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 with Z
            "%Y-%m-%dT%H:%M:%S",      # ISO 8601 without Z or ms
            "%Y-%m-%d %H:%M:%S",      # Common datetime format
            "%Y-%m-%d",               # Date only
        ]
        for fmt in formats_to_try:
            try:
                return datetime.datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        # As a fallback for date-only strings that might not have matched,
        # try appending a default time if it looks like just a date.
        if "T" not in date_string and " " not in date_string: # Likely just a date
             try:
                 # Attempt to parse as date and then combine with min time
                 dt_date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
                 return datetime.datetime.combine(dt_date, datetime.time.min)
             except ValueError:
                 pass # Fall through to raise error

        raise ValueError(f"Could not parse date string '{date_string}'. Please use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD HH:MM:SS.")


    def generate(self, execution_context: Optional[Any] = None, **kwargs) -> Any:
        rand_instance = random # Default to global random
        if execution_context and hasattr(execution_context, 'get_seeded_random_instance'):
            rand_instance = execution_context.get_seeded_random_instance()

        # Convert dates to timestamps (seconds since epoch)
        start_ts = self.start_date.timestamp()
        end_ts = self.end_date.timestamp()

        # Generate a random timestamp between start_ts and end_ts
        random_ts = rand_instance.uniform(start_ts, end_ts)

        # Convert the random timestamp back to a datetime object
        generated_datetime = datetime.datetime.fromtimestamp(random_ts)

        if self.format_string:
            try:
                return generated_datetime.strftime(self.format_string)
            except ValueError as e: # Catch potential errors from invalid format string characters on some platforms
                raise ValueError(f"Invalid format string '{self.format_string}' for strftime: {e}")
        else:
            # Default to ISO 8601 format if no format_string is provided
            return generated_datetime.isoformat()

    @classmethod
    def _validate_datetime_string(cls, dt_str: str, field_name: str, entity_name: str, current_field: str) -> datetime.datetime:
        # Reusing the parsing logic from __init__ for validation
        try:
            return cls._parse_datetime_flexible_static(dt_str)
        except ValueError as e: # This e already contains a good message from _parse_datetime_flexible_static
            raise BlueprintValidationError(
                f"In entity '{entity_name}', field '{current_field}': "
                f"Invalid format for timestamp setting '{field_name}'. Value provided: '{dt_str}'.\n"
                f"Reason: {e}\n" # Includes detailed parsing error
                f"Expected formats include YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, or YYYY-MM-DD HH:MM:SS."
            )

    @staticmethod
    def _parse_datetime_flexible_static(date_string: str) -> datetime.datetime:
        """Tries to parse a date string using common date and datetime formats. Static version."""
        formats_to_try = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 with Z
            "%Y-%m-%dT%H:%M:%S",      # ISO 8601 without Z or ms
            "%Y-%m-%d %H:%M:%S",      # Common datetime format
            "%Y-%m-%d",               # Date only
        ]
        for fmt in formats_to_try:
            try:
                return datetime.datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        if "T" not in date_string and " " not in date_string: # Likely just a date
             try:
                 dt_date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
                 return datetime.datetime.combine(dt_date, datetime.time.min)
             except ValueError:
                 pass
        raise ValueError(f"Could not parse date string '{date_string}'. Please use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD HH:MM:SS.")


    @classmethod
    def validate_config(cls, config: dict, all_blueprint_data: dict, current_entity_name: str, current_field_name: str) -> None:
        for key in ['start_date', 'end_date']:
            if key not in config:
                raise BlueprintValidationError(
                    f"In entity '{current_entity_name}', field '{current_field_name}': "
                    f"TimestampGenerator is missing the required '{key}' setting.\n"
                    f"Example: {key}: \"YYYY-MM-DD\""
                )
            if not isinstance(config[key], str):
                val = config[key]
                raise BlueprintValidationError(
                    f"In entity '{current_entity_name}', field '{current_field_name}': "
                    f"TimestampGenerator setting '{key}' must be a string. Found: '{val}' (type: {type(val).__name__}).\n"
                    f"Example: {key}: \"YYYY-MM-DD\""
                )

        start_dt_str = config['start_date']
        end_dt_str = config['end_date']

        start_dt = cls._validate_datetime_string(start_dt_str, 'start_date', current_entity_name, current_field_name)
        end_dt = cls._validate_datetime_string(end_dt_str, 'end_date', current_entity_name, current_field_name)

        if start_dt >= end_dt:
            raise BlueprintValidationError(
                f"In entity '{current_entity_name}', field '{current_field_name}': "
                f"TimestampGenerator setting 'start_date' ('{start_dt_str}') must be before 'end_date' ('{end_dt_str}')."
            )

        if 'format' in config:
            format_val = config['format']
            if not isinstance(format_val, str):
                raise BlueprintValidationError(
                    f"In entity '{current_entity_name}', field '{current_field_name}': "
                    f"TimestampGenerator setting 'format' must be a string if provided (e.g., \"%Y-%m-%d %H:%M\"). Found: '{format_val}' (type: {type(format_val).__name__})."
                )
        # Further validation of the format string itself (e.g., valid strftime directives) can be complex.

class RefGenerator(Generator):
    def __init__(self, config: dict):
        self.ref_string = config.get('ref')
        self.use_record_from_field = config.get('use_record_from')
        self.field_to_get = config.get('field_to_get')

        if self.use_record_from_field:
            if not self.field_to_get:
                raise ValueError("'field_to_get' must be specified when 'use_record_from' is used.")
            if self.ref_string:
                raise ValueError("'ref' cannot be used simultaneously with 'use_record_from'.")
        elif not self.ref_string:
            raise ValueError("RefGenerator config must include either 'ref' or 'use_record_from' key.")

    def generate(self, execution_context: Any = None, current_row_data: Optional[Dict[str, Any]] = None,
                 current_entity_name: Optional[str] = None, current_row_index: Optional[int] = None,
                 current_field_name: Optional[str] = None) -> Any:
        if not execution_context or not hasattr(execution_context, 'get_generated_data') \
           or not hasattr(execution_context, 'cache_referred_record') \
           or not hasattr(execution_context, 'get_cached_referred_record'):
            raise ValueError("ExecutionContext with required methods is needed for RefGenerator.")

        if self.use_record_from_field:
            # This is a secondary reference, using a cached record
            if current_entity_name is None or current_row_index is None:
                raise ValueError("current_entity_name and current_row_index are required for secondary reference.")

            cached_record = execution_context.get_cached_referred_record(
                current_entity_name, current_row_index, self.use_record_from_field
            )

            if not cached_record:
                raise ValueError(
                    f"No cached record found for source field '{self.use_record_from_field}' "
                    f"in entity '{current_entity_name}' at row {current_row_index}. "
                    f"Ensure '{self.use_record_from_field}' is a 'ref' field defined before this one."
                )

            if self.field_to_get not in cached_record:
                raise ValueError(
                    f"Field '{self.field_to_get}' not found in the cached record from "
                    f"source field '{self.use_record_from_field}'. Cached record keys: {list(cached_record.keys())}"
                )

            return cached_record[self.field_to_get]
        else:
            # This is a primary reference, fetches and caches a record
            if not self.ref_string or '.' not in self.ref_string:
                raise ValueError(f"Invalid ref_string format: '{self.ref_string}'. Expected 'entity_name.field_name'.")

            entity_name, field_name = self.ref_string.split('.', 1)

        if not execution_context or not hasattr(execution_context, 'get_generated_data'):
            # This case handles when execution_context is not provided or doesn't have the expected method.
            # Depending on strictness, this could raise an error or return a specific signal.
            # For now, let's assume if no context, we can't proceed.
            raise ValueError("ExecutionContext with get_generated_data method is required for RefGenerator.")

        try:
            referenced_entity_data: List[Dict[str, Any]] = execution_context.get_generated_data(entity_name)
        except Exception as e: # Broad catch if get_generated_data itself raises an error (e.g., entity not found by it)
            raise ValueError(f"Failed to retrieve data for entity '{entity_name}' from execution_context: {e}")


        if not referenced_entity_data:
            # If the entity exists but has no data, this is a distinct case.
            # Depending on requirements, this could be an error or could return None/default.
            # For now, let's treat it as an issue if we expect data.
            # Alternatively, could return None or a specific marker.
            raise ValueError(f"No data found for referenced entity '{entity_name}'.")

        # Retrieve a random record from the list of records for the entity
        rand_instance = random # Default to global random
        if execution_context and hasattr(execution_context, 'get_seeded_random_instance'):
            rand_instance = execution_context.get_seeded_random_instance()

        selected_record: Dict[str, Any] = rand_instance.choice(referenced_entity_data)

        if field_name not in selected_record:
            raise ValueError(f"Field '{field_name}' not found in the selected record from entity '{entity_name}'. Record: {selected_record}")

        # Cache the selected record for potential use by other fields in the same row
        if current_entity_name is not None and current_row_index is not None and current_field_name is not None:
            execution_context.cache_referred_record(
                current_entity_name, current_row_index, current_field_name, selected_record
            )
        else:
            # This might happen if called in a context where these are not provided (e.g. older tests not updated yet)
            # Depending on strictness, could raise an error or log a warning.
            # For now, we'll allow it but caching won't occur.
            pass # Or log a warning: "Caching skipped for primary ref due to missing context details."


        return selected_record[field_name]

    @classmethod
    def validate_config(cls, config: dict, all_blueprint_data: dict, current_entity_name: str, current_field_name: str) -> None:
        has_ref = 'ref' in config
        has_use_record_from = 'use_record_from' in config
        has_field_to_get = 'field_to_get' in config

        field_loc = f"In entity '{current_entity_name}', field '{current_field_name}' (RefGenerator)"

        if has_ref and has_use_record_from:
            raise BlueprintValidationError(
                f"{field_loc}: Settings 'ref' and 'use_record_from' cannot be used together. Please choose one."
            )

        if has_use_record_from:
            use_record_from_val = config['use_record_from']
            if not has_field_to_get:
                raise BlueprintValidationError(
                    f"{field_loc}: When 'use_record_from' is specified ('{use_record_from_val}'), "
                    f"'field_to_get' is also required to specify which field from the referenced record to use."
                )
            if not isinstance(use_record_from_val, str):
                raise BlueprintValidationError(
                    f"{field_loc}: Setting 'use_record_from' must be a string (the name of another field in the same entity). "
                    f"Found: '{use_record_from_val}' (type: {type(use_record_from_val).__name__})."
                )

            field_to_get_val = config['field_to_get']
            if not isinstance(field_to_get_val, str):
                 raise BlueprintValidationError(
                    f"{field_loc}: Setting 'field_to_get' must be a string (the name of a field in the referenced entity). "
                    f"Found: '{field_to_get_val}' (type: {type(field_to_get_val).__name__})."
                )

            current_entity_fields = all_blueprint_data.get(current_entity_name, {}).get('fields', {})
            if use_record_from_val not in current_entity_fields:
                available_fields_str = ", ".join(sorted(current_entity_fields.keys())) if current_entity_fields else "none"
                raise BlueprintValidationError(
                    f"{field_loc}: The field '{use_record_from_val}' specified in 'use_record_from' was not found in the current entity '{current_entity_name}'.\n"
                    f"Available fields in '{current_entity_name}': {available_fields_str}."
                )
            # Note: Validating that 'use_record_from_val' itself points to a primary ref, and validating
            # 'field_to_get_val' against the schema of the *eventual* target entity is complex for static validation.
            # The current checks ensure the immediate structure is valid.

        elif has_ref:
            ref_string = config['ref']
            if not isinstance(ref_string, str) or '.' not in ref_string:
                raise BlueprintValidationError(
                    f"{field_loc}: Setting 'ref' ('{ref_string}') is invalid. "
                    f"It must be a string in the format 'entity_name.field_name'.\n"
                    f"Example: ref: \"other_entity.id\""
                )

            entity_name_to_ref, field_name_to_ref = ref_string.split('.', 1)

            if entity_name_to_ref not in all_blueprint_data:
                available_entities_str = ", ".join(sorted(all_blueprint_data.keys())) if all_blueprint_data else "none"
                raise BlueprintValidationError(
                    f"{field_loc}: The entity '{entity_name_to_ref}' referenced in '{ref_string}' was not found in your blueprint.\n"
                    f"Available entities are: {available_entities_str}."
                )

            referenced_entity_config = all_blueprint_data.get(entity_name_to_ref, {})
            referenced_entity_fields = referenced_entity_config.get('fields', {})

            if field_name_to_ref not in referenced_entity_fields:
                available_fields_str = ", ".join(sorted(referenced_entity_fields.keys())) if referenced_entity_fields else "none"
                raise BlueprintValidationError(
                    f"{field_loc}: The field '{field_name_to_ref}' referenced in '{ref_string}' was not found in entity '{entity_name_to_ref}'.\n"
                    f"Available fields in '{entity_name_to_ref}' are: {available_fields_str}."
                )
        else:
            raise BlueprintValidationError(
                f"{field_loc}: Configuration is missing. It must include either 'ref' (for a direct reference to another entity's field) "
                f"or both 'use_record_from' and 'field_to_get' (to get a field from a record already referenced by another field in this entity)."
            )

class ExprGenerator(Generator):
    def __init__(self, config: dict):
        self.expression = config.get('expression')
        if not self.expression:
            raise ValueError("ExprGenerator config must include 'expression' key.")

        self.asteval_interpreter = Interpreter()
        # Pre-compile the expression if possible, or store it for evaluation
        # For asteval, evaluation happens on the fly, but the interpreter is set up once.

    def _get_random_choice_from_entity(self, execution_context: Any, entity_name: str, rand_instance: random.Random) -> Optional[Dict[str, Any]]:
        """Helper to get a random record from a referenced entity, using a specific random instance."""
        if not execution_context or not hasattr(execution_context, 'get_generated_data'):
            # This might happen if called in a context where these are not provided
            # Log a warning or raise an error based on strictness.
            # For now, let's return None, expressions can handle it.
            # self.asteval_interpreter.error_msg = f"ExecutionContext not available for ref_one('{entity_name}')"
            # return None # Or raise an error that asteval can catch
            # Consider logging instead of printing for production code:
            # import logging
            # logging.warning(f"ExecutionContext not available for ref_one('{entity_name}')")
            return None

        referenced_entity_data: Optional[List[Dict[str, Any]]] = execution_context.get_generated_data(entity_name)

        if not referenced_entity_data:
            # self.asteval_interpreter.error_msg = f"No data found for referenced entity '{entity_name}' in ref_one."
            # return None
            # logging.warning(f"No data found for referenced entity '{entity_name}' in ref_one.")
            return None # Expression can handle NoneType, e.g., `(ref_one('X') or {}).get('field')`

        return rand_instance.choice(referenced_entity_data)

    def _get_all_records_from_entity(self, execution_context: Any, entity_name: str) -> List[Dict[str, Any]]:
        """Helper to get all records from a referenced entity."""
        if not execution_context or not hasattr(execution_context, 'get_generated_data'):
            # self.asteval_interpreter.error_msg = f"ExecutionContext not available for ref_all('{entity_name}')"
            # return []
            # logging.warning(f"ExecutionContext not available for ref_all('{entity_name}')")
            return []

        referenced_entity_data: Optional[List[Dict[str, Any]]] = execution_context.get_generated_data(entity_name)

        return referenced_entity_data if referenced_entity_data else []

    def generate(self, current_row_data: Optional[Dict[str, Any]] = None,
                 execution_context: Optional[Any] = None, **kwargs) -> Any:
        if current_row_data is None:
            current_row_data = {}

        # Prepare the symbol table for asteval
        # Note: asteval_interpreter can be created here if it needs to be stateless per call,
        # or reused if it's safe (generally it is, but symtable needs to be fresh).
        # Re-creating or clearing symtable for each call is safer.
        # self.asteval_interpreter.symtable.clear() # If reusing interpreter instance's symtable
        # Or, create a new one each time if preferred, to ensure no state leakage between generate calls
        # current_interpreter = Interpreter() # If creating new each time

        # For now, reusing self.asteval_interpreter but setting its symtable fresh each time.
        # This is okay as long as the expression itself doesn't modify the interpreter's state in unwanted ways.
        # asteval is designed to be safe for re-evaluation with new symbol tables.

        rand_instance = random # Default to global random
        if execution_context and hasattr(execution_context, 'get_seeded_random_instance'):
            rand_instance = execution_context.get_seeded_random_instance()

        symtable = {
            'current': current_row_data,
            'self': current_row_data,
            'this': current_row_data,
            'ref_one': lambda entity_name_str: self._get_random_choice_from_entity(execution_context, entity_name_str, rand_instance),
            'ref_all': lambda entity_name_str: self._get_all_records_from_entity(execution_context, entity_name_str),
            'random': rand_instance, # Expose the potentially seeded random instance
            'sum': sum,
            'len': len,
            'min': min,
            'max': max,
            'str': str,
            'int': int,
            'float': float,
            'decimal': decimal,
            'bool': bool,
            'list': list,
            'dict': dict,
            'math': math,
            'round': round,
            'abs': abs,
            'datetime': datetime,
            'uuid4': uuid.uuid4,
            'isinstance': isinstance,
            #Utilities
        }

        self.asteval_interpreter.symtable = symtable # Set fresh symtable for this evaluation

        # Evaluate the expression
        # Use a fresh interpreter for each call to ensure no state leaks if preferred.
        # For now, reusing the instance's interpreter but with a fresh symtable.
        result = self.asteval_interpreter.eval(self.expression)

        # Check for errors
        if self.asteval_interpreter.error:
            error_messages = []
            for error in self.asteval_interpreter.error:
                error_messages.append(str(error.get_error()))

            error_details = "; ".join(error_messages)
            # Clear errors for next use if the interpreter instance is reused.
            self.asteval_interpreter.error = []
            self.asteval_interpreter.error_msg = ''

            raise GeneratorError(
                message=f"Error evaluating expression: {error_details}",
                generator_name='ExprGenerator',
                expression=self.expression
            )

        return result

    @classmethod
    def validate_config(cls, config: dict, all_blueprint_data: dict, current_entity_name: str, current_field_name: str) -> None:
        field_loc = f"In entity '{current_entity_name}', field '{current_field_name}' (ExprGenerator)"
        if 'expression' not in config:
            raise BlueprintValidationError(
                f"{field_loc}: Missing the required 'expression' setting.\n"
                f"This setting should contain the Python-like expression to evaluate.\n"
                f"Example: expression: \"current.price * current.quantity\""
            )

        expression_val = config['expression']
        if not isinstance(expression_val, str):
            raise BlueprintValidationError(
                f"{field_loc}: Setting 'expression' must be a string. Found: '{expression_val}' (type: {type(expression_val).__name__}).\n"
                f"Example: expression: \"(current.value_a + current.value_b) / 2\""
            )
        # Static analysis of the expression string for syntax correctness is complex here.
        # asteval will catch syntax errors during its evaluation phase.


class EnumGenerator(Generator):
    def __init__(self, config: dict):
        self.values = config.get('values')
        if not self.values:
            raise ValueError("EnumGenerator config must include 'values' key with a non-empty list.")
        if not isinstance(self.values, list) or len(self.values) == 0:
            raise ValueError("'values' must be a non-empty list.")
        self.current_index = 0

    def generate(self, **kwargs) -> Any:
        if not self.values: # Should be caught by constructor, but as a safeguard
            return None
        value = self.values[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.values)
        return value

    @classmethod
    def validate_config(cls, config: dict, all_blueprint_data: dict, current_entity_name: str, current_field_name: str) -> None:
        field_loc = f"In entity '{current_entity_name}', field '{current_field_name}' (EnumGenerator)"
        if 'values' not in config:
            raise BlueprintValidationError(
                f"{field_loc}: Missing the required 'values' setting.\n"
                f"This setting should be a list of possible values for the enumeration.\n"
                f"Example: values: [\"active\", \"pending\", \"expired\"]"
            )

        values_val = config['values']
        if not isinstance(values_val, list) or not values_val:
            raise BlueprintValidationError(
                f"{field_loc}: Setting 'values' must be a non-empty list. Found: '{values_val}'.\n"
                f"Example: values: [\"option1\", \"option2\"]"
            )
