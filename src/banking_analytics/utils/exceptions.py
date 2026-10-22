"""Custom exceptions for Banking Customer Analytics & Risk Engine."""


class BankingAnalyticsError(Exception):
    """Base exception for all domain-specific errors in banking_analytics."""

    def __init__(self, message: str, module: str = "", action: str = ""):
        self.message = message
        self.module = module
        self.action = action
        full_msg = message
        if module:
            full_msg = f"[{module}] {full_msg}"
        if action:
            full_msg = f"{full_msg}\nAction required: {action}"
        super().__init__(full_msg)


class SchemaValidationError(BankingAnalyticsError):
    """Raised when required columns are missing or schema does not match specification."""

    def __init__(self, message: str, module: str = "data_loader.validate_schema", action: str = "Verify input CSV matches required schema defined in config/config.yaml."):
        super().__init__(message=message, module=module, action=action)


class DataIntegrityError(BankingAnalyticsError):
    """Raised when target variable contains nulls or critical data quality checks fail."""

    def __init__(self, message: str, module: str = "data_cleaner", action: str = "Inspect raw data for missing target values or corruption."):
        super().__init__(message=message, module=module, action=action)


class DataSufficiencyError(BankingAnalyticsError):
    """Raised when cleaned dataset has fewer rows than the minimum threshold."""

    def __init__(self, message: str, module: str = "data_cleaner", action: str = "Ensure sufficient raw data rows exist after filtering and cleaning."):
        super().__init__(message=message, module=module, action=action)


class DBConnectionError(BankingAnalyticsError):
    """Raised when database connection fails. Suggests DuckDB fallback."""

    def __init__(self, message: str, module: str = "db_loader", action: str = "Ensure PostgreSQL server is running or set database.backend to 'duckdb' in config/config.yaml."):
        super().__init__(message=message, module=module, action=action)


class PipelineConfigError(BankingAnalyticsError):
    """Raised when configuration file is missing or has missing required keys."""

    def __init__(self, message: str, module: str = "config_loader", action: str = "Verify config/config.yaml exists and contains all required configuration sections."):
        super().__init__(message=message, module=module, action=action)
