from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.progress import Progress, TaskID
from mockingbird.output.formatters import OutputFormatter, DuckDBFormatter

class OutputService:
    def __init__(self, progress: Progress, task_id: TaskID):
        self.progress = progress
        self.task_id = task_id
        self._formatters: Dict[str, OutputFormatter] = {
            "csv": DuckDBFormatter("csv"),
            "parquet": DuckDBFormatter("parquet"),
            "json": DuckDBFormatter("json"),
        }

    def get_formatter(self, format_name: str) -> OutputFormatter:
        formatter = self._formatters.get(format_name.lower())
        if not formatter:
            raise ValueError(f"Unsupported output format: {format_name}. Supported formats are: {', '.join(self._formatters.keys())}")
        return formatter

    def export_data_entity(
        self,
        entity_name: str,
        entity_data: List[Dict[str, Any]],
        formatter: OutputFormatter,
        output_dir: Path
    ) -> None:
        """
        Exports data for a single entity using the provided formatter.
        """
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Error creating output directory {output_dir}: {e}")
                # Potentially re-raise or handle more gracefully
                return

        column_order: Optional[List[str]] = None
        if entity_data: # If there's data, determine column order from first record
            column_order = list(entity_data[0].keys())
            # Future enhancement: Allow user to specify column order in blueprint

        try:
            formatter.format_data(entity_name, entity_data, output_dir, column_order=column_order)
            # Removed duplicate print statement, format_data in formatter already prints
            # print(f"Data for entity '{entity_name}' exported to {output_dir} using {formatter.__class__.__name__}")
        except Exception as e:
            print(f"Error during formatting/export of entity '{entity_name}': {e}")
            # Potentially re-raise

    def export_all_data(
        self,
        all_generated_data: Dict[str, List[Dict[str, Any]]],
        format_name: str,
        output_dir: Path
    ) -> None:
        """
        Exports all generated data (multiple entities) to the specified directory and format.
        """
        formatter = self.get_formatter(format_name)
        if not all_generated_data:
            self.progress.update(self.task_id, description="No data to export.")
            return

        for entity_name, entity_data_list in all_generated_data.items():
            task_description = f"Exporting {entity_name} to {format_name}"
            self.progress.update(self.task_id, description=task_description)

            entity_task = self.progress.add_task(f"  - {entity_name}", total=1, indent=2)

            self.export_data_entity(entity_name, entity_data_list, formatter, output_dir)

            self.progress.update(entity_task, advance=1)
            self.progress.update(self.task_id, advance=1)
            self.progress.update(entity_task, description=f"✅ {entity_name}")
