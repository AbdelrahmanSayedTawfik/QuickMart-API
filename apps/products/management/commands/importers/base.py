import csv
from abc import ABC, abstractmethod
from django.db import transaction


class BaseImporter(ABC):

    REQUIRED_COLUMNS: list[str] = []
    OPTIONAL_COLUMNS: list[str] = []

    def __init__(self, stdout, style, user=None):
        
        self.stdout = stdout
        self.style  = style
        self.user   = user

    def run(self, file_path: str, skip_invalid: bool, update_existing: bool) -> None:

        rows, columns = self._read_file(file_path)
        if rows is None:
            return

        if not self._validate_columns(columns):
            return
        
        self.check_permission()
        self._process_rows(rows, skip_invalid, update_existing)


    @abstractmethod
    def check_permission(self) -> None:
        """
        Validate that self.user has permission to run this import.
        Called ONCE before any rows are touched.
        Raise ValueError with a clear message if permission is denied.
        """

    @abstractmethod
    def import_row(self, row: dict, row_num: int, update_existing: bool) -> str:
        """
        Process a single CSV row.
        Return  : 'created' | 'updated' | 'skipped'
        Raise   : ValueError with a clear message on invalid data
        """

    def _read_file(self, file_path: str) -> tuple:
        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader  = csv.DictReader(f)
                rows    = list(reader)
                columns = reader.fieldnames or []
            self.stdout.write(
                self.style.NOTICE(f'Read {len(rows)} rows from {file_path}')
            )
            return rows, columns
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return None, None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to read file: {e}'))
            return None, None

    def _validate_columns(self, columns: list) -> bool:
        missing = [col for col in self.REQUIRED_COLUMNS if col not in columns]
        if missing:
            self.stdout.write(self.style.ERROR(
                f'Missing required columns : {", ".join(missing)}\n'
                f'Your CSV has             : {", ".join(columns)}\n'
                f'Required                 : {", ".join(self.REQUIRED_COLUMNS)}'
            ))
            return False
        return True

    def _process_rows(
        self,
        rows          : list,
        skip_invalid  : bool,
        update_existing: bool,
    ) -> None:
        created = updated = skipped = errors = 0
        error_list: list[str] = []

        for index, row in enumerate(rows):
            row_num = index + 2  # row 1 is the header
            try:
                with transaction.atomic():
                    result = self.import_row(row, row_num, update_existing)

                if result == 'created':
                    created += 1
                elif result == 'updated':
                    updated += 1
                elif result == 'skipped':
                    skipped += 1

            except Exception as e:
                errors += 1
                msg = f'Row {row_num}: {e}'
                error_list.append(msg)
                self.stdout.write(self.style.ERROR(f'  {msg}'))

                if not skip_invalid:
                    self.stdout.write(self.style.ERROR(
                        f'Stopping at row {row_num}. '
                        f'Use --skip-invalid to continue past errors.'
                    ))
                    break

        total = created + updated + skipped + errors
        self.stdout.write(self.style.SUCCESS(
            f'\n{"=" * 50}\n'
            f'IMPORT SUMMARY\n'
            f'{"=" * 50}\n'
            f'Created : {created}\n'
            f'Updated : {updated}\n'
            f'Skipped : {skipped}\n'
            f'Errors  : {errors}\n'
            f'Total   : {total} / {len(rows)}\n'
            f'{"=" * 50}'
        ))

        if error_list:
            self.stdout.write(self.style.WARNING('\nError Details:'))
            for err in error_list:
                self.stdout.write(self.style.WARNING(f'  - {err}'))

    # -------------------------------------------------------------- #
    # Data extraction helpers (available to all subclasses)          #
    # -------------------------------------------------------------- #

    def get(self, row: dict, column: str, default: str = '') -> str:
        """Read a string value from a CSV row. Returns default if empty."""
        value = row.get(column, default)
        if value is None:
            return default
        value = str(value).strip()
        return value if value not in ('', 'nan', 'None') else default

    def get_decimal(self, row: dict, column: str, default=0):
        """Read a Decimal value. Raises ValueError on invalid input."""
        from decimal import Decimal, InvalidOperation
        value = self.get(row, column, '')
        if not value:
            return Decimal(str(default))
        try:
            return Decimal(str(value))
        except InvalidOperation:
            raise ValueError(
                f'Column "{column}" must be a number, got: "{value}"'
            )

    def get_int(self, row: dict, column: str, default: int = 0) -> int:
        """Read an integer value. Raises ValueError on invalid input."""
        value = self.get(row, column, '')
        if not value:
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            raise ValueError(
                f'Column "{column}" must be a whole number, got: "{value}"'
            )

    def get_bool(self, row: dict, column: str, default: bool = True) -> bool:
        """Read a boolean value. Accepts true/false/yes/no/1/0."""
        value = self.get(row, column, '').lower()
        if not value:
            return default
        if value in ('true', 'yes', '1', 't', 'y'):
            return True
        if value in ('false', 'no', '0', 'f', 'n'):
            return False
        raise ValueError(
            f'Column "{column}" must be true/false, got: "{value}"'
        )