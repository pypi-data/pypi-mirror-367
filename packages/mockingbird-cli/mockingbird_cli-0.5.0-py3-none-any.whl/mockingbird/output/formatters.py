from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import duckdb
import pandas as pd

class OutputFormatter(ABC):
    @abstractmethod
    def format_data(self, entity_name: str, data: List[Dict[str, Any]], output_path: Path, column_order: Optional[List[str]] = None) -> None:
        """
        Formats and writes data for a single entity to the specified path.
        'column_order' can be used to ensure consistent CSV column ordering if provided.
        """
        pass

class DuckDBFormatter(OutputFormatter):
    def __init__(self, file_format: str):
        self.file_format = file_format.lower()

    def format_data(self, entity_name: str, data: List[Dict[str, Any]], output_path: Path, column_order: Optional[List[str]] = None) -> None:
        file_path = output_path / f"{entity_name}.{self.file_format}"

        if not data:
            print(f"No data for {entity_name}, {self.file_format} file not created: {file_path}")
            return

        df = pd.DataFrame(data)
        if column_order:
            df = df[column_order]

        con = duckdb.connect(database=':memory:', read_only=False)
        con.register(f'{entity_name}_df', df)
        con.execute(f"COPY {entity_name}_df TO '{file_path}' (FORMAT '{self.file_format.upper()}')")
        con.close()

