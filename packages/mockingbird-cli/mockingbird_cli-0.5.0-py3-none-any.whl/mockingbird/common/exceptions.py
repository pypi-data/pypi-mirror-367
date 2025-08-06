class BlueprintValidationError(ValueError):
    """Custom exception for errors found during blueprint validation."""
    pass

class GeneratorError(Exception):
    """Custom exception for errors that occur during data generation."""
    def __init__(self, message, generator_name=None, expression=None):
        full_message = f"Generator '{generator_name}': {message}"
        if expression:
            full_message += f"\nExpression: {expression}"
        super().__init__(full_message)
        self.generator_name = generator_name
        self.expression = expression
