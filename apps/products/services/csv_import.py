# apps/products/services/csv_import.py

import io
import csv
from typing import Type
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile


class ImportResult:
    def __init__(self):
        self.created_count  : int       = 0
        self.updated_count  : int       = 0
        self.skipped_count  : int       = 0
        self.error_count    : int       = 0
        self.error_details  : list[str] = []
        self.total_rows     : int       = 0
        self.success        : bool      = False
        self.message        : str       = ''

    def to_dict(self) -> dict:
        return {
            'success'      : self.success,
            'message'      : self.message,
            'created'      : self.created_count,
            'updated'      : self.updated_count,
            'skipped'      : self.skipped_count,
            'errors'       : self.error_count,
            'total_rows'   : self.total_rows,
            'error_details': self.error_details,
        }

class CSVImportService:

    _importers: dict[str, Type] = {}

    @classmethod
    def register_importer(cls, model_name: str, importer_class: Type) -> None:
        """Register an importer class under a model name key."""
        cls._importers[model_name] = importer_class

    @classmethod
    def get_available_models(cls) -> list[str]:
        """Return all registered model names."""
        return list(cls._importers.keys())

    @classmethod
    def get_template_columns(cls, model_name: str) -> dict | None:

        if model_name not in cls._importers:
            return None

        importer_class = cls._importers[model_name]
        return {
            'required': importer_class.REQUIRED_COLUMNS,
            'optional': importer_class.OPTIONAL_COLUMNS,
        }

    @classmethod
    def import_from_file(
        cls,
        model_name      : str,
        uploaded_file   : UploadedFile,
        user            = None,
        skip_invalid    : bool = False,
        update_existing : bool = False,
    ) -> ImportResult:

        result = ImportResult()

        # Step 1 — validate model name
        if model_name not in cls._importers:
            result.message = (
                f"Unknown model '{model_name}'. "
                f"Available models: {', '.join(cls._importers.keys())}"
            )
            return result

        importer = cls._importers[model_name](
            stdout=None,
            style=None,
            user=user,
        )

        # Step 2 — check permission once before touching any rows
        try:
            importer.check_permission()
        except ValueError as e:
            result.message = str(e)
            return result

        # Step 3 — read and decode the uploaded file
        try:
            file_content = uploaded_file.read().decode('utf-8')
            csv_file     = io.StringIO(file_content)
        except UnicodeDecodeError:
            result.message = 'File must be UTF-8 encoded.'
            return result
        except Exception as e:
            result.message = f'Failed to read file: {e}'
            return result

        # Step 4 — parse CSV and validate required columns
        try:
            # Read all lines, skip the hints row (row 2), keep header + data
            lines = csv_file.readlines()
            if len(lines) < 2:
                result.message = 'CSV file is empty or missing data.'
                return result
    
            # lines[0] = headers, lines[1] = hints, lines[2+] = data
            data_lines = [lines[0]] + lines[2:]
            csv_file = io.StringIO(''.join(data_lines))
    
            reader = csv.DictReader(csv_file)
            rows = list(reader)
            columns = reader.fieldnames or []
            result.total_rows = len(rows)

            missing = [
                col for col in importer.REQUIRED_COLUMNS
                if col not in columns
            ]
            if missing:
                result.message = f"Missing required columns: {', '.join(missing)}"
                result.error_details.append(
                    f"Your CSV has : {', '.join(columns)}"
                )
                result.error_details.append(
                    f"Required     : {', '.join(importer.REQUIRED_COLUMNS)}"
                )
                return result

        except Exception as e:
            result.message = f'Failed to parse CSV: {e}'
            return result

        # Step 5 — process each row
        for index, row in enumerate(rows):
            row_num = index + 3
            try:
                with transaction.atomic():
                    row_result = importer.import_row(row, row_num, update_existing)

                if row_result == 'created':
                    result.created_count += 1
                elif row_result == 'updated':
                    result.updated_count += 1
                elif row_result == 'skipped':
                    result.skipped_count += 1

            except Exception as e:
                result.error_count += 1
                result.error_details.append(f'Row {row_num}: {e}')

                if not skip_invalid:
                    result.message = (
                        f'Stopped at row {row_num}. '
                        f'Pass skip_invalid=true to continue past errors.'
                    )
                    break

        # Step 6 — build final result
        result.success = (result.error_count == 0) or skip_invalid
        result.message = result.message or 'Import completed successfully.'
        return result