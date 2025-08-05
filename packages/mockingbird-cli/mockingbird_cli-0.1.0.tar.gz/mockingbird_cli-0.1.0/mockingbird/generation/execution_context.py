from typing import Optional, Any, Dict, List
# import duckdb # Would be imported if DuckDB was being used for real
from mockingbird.generation.generators import GeneratorRegistry
import random # For the seed_random_instance method

class ExecutionContext:
    def __init__(self, seed: Optional[int] = None):
        self.seed: Optional[int] = seed
        # self.db_connection = duckdb.connect(database=':memory:', read_only=False) # Dummy
        self._generator_registry: GeneratorRegistry = GeneratorRegistry()
        self._generated_data_store: Dict[str, List[Dict[str, Any]]] = {}
        # Cache for records selected by RefGenerator instances
        # Key: (generating_entity_name, row_index, current_field_name_of_ref_generator)
        # Value: The actual record (dictionary) selected from the referred entity
        self._referred_records_cache: Dict[tuple[str, int, str], Dict[str, Any]] = {}

        self._seeded_random_instance: Optional[random.Random] = None

        # Global seeding for 'random' module if a seed is provided.
        # Individual generators like Faker handle their own seeding internally if they see self.seed.
        if self.seed is not None:
            random.seed(self.seed) # Seed the global random instance
            self._seeded_random_instance = random.Random(self.seed)
        else:
            # If no seed, initialize with a new Random instance (unseeded, but isolated)
            self._seeded_random_instance = random.Random()

    def get_seeded_random_instance(self) -> random.Random:
        """
        Returns a random.Random instance.
        If a seed was provided to ExecutionContext, this instance will be seeded.
        Otherwise, it's an unseeded random.Random instance isolated from global `random`.
        """
        # This instance is initialized in __init__, so it's always available.
        return self._seeded_random_instance

    def set_generated_data_store(self, data_store: Dict[str, List[Dict[str, Any]]]):
        self._generated_data_store = data_store

    def get_generated_data(self, entity_name: str) -> Optional[List[Dict[str, Any]]]:
        return self._generated_data_store.get(entity_name)

    def get_db_connection(self) -> Any: # Should return duckdb.DuckDBPyConnection
        # return self.db_connection
        return "dummy_duckdb_connection" # Remains dummy for now

    def get_generator_registry(self) -> GeneratorRegistry:
        return self._generator_registry

    def seed_random_instance(self, random_instance: Any):
        """
        Seeds a specific instance of random.Random if a seed is set in the context.
        Useful for generators that might use their own random.Random() instances.
        However, many generators (like 'random.choice') use the global 'random' module,
        which is seeded in __init__.
        This method is more for custom random instances.
        For now, we'll assume generators use the global 'random' or handle seeding via Faker's own mechanism.
        If a generator specifically needs to seed its own 'random.Random()' object, it can call this.
        """
        if self.seed is not None and hasattr(random_instance, 'seed'):
            random_instance.seed(self.seed)

    def cache_referred_record(
        self,
        generating_entity_name: str,
        row_idx: int,
        current_field_name: str,
        record: Dict[str, Any]
    ) -> None:
        """Caches a record selected by a RefGenerator for potential use by other RefGenerators in the same row."""
        cache_key = (generating_entity_name, row_idx, current_field_name)
        self._referred_records_cache[cache_key] = record

    def get_cached_referred_record(
        self,
        generating_entity_name: str,
        row_idx: int,
        source_field_name_referenced: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a cached record that was stored by a RefGenerator associated with source_field_name_referenced."""
        cache_key = (generating_entity_name, row_idx, source_field_name_referenced)
        return self._referred_records_cache.get(cache_key)

    def close(self):
        # if self.db_connection:
        #     self.db_connection.close()
        pass
