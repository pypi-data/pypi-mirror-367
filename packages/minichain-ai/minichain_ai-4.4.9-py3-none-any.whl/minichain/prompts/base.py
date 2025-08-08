# src/minichain/prompts/base.py
"""
Defines the abstract base class for all prompt templates in the Mini-Chain framework.
This ensures a consistent interface for formatting and validation across different
prompting strategies.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BasePromptTemplate(ABC):
    """Abstract base class for prompt templates."""

    def __init__(self, input_variables: List[str]):
        """
        Initializes the template with a list of expected input variables.

        Args:
            input_variables (List[str]): A list of variable names that the
                template expects for formatting (e.g., ["context", "question"]).
        """
        self.input_variables = input_variables

    @abstractmethod
    def format(self, **kwargs: Any) -> Any:
        """
        Formats the prompt with the given variables.

        The return type can be a string or a structured object (like a list of
        messages), depending on the template type.
        """
        pass

    def invoke(self, variables: Dict[str, Any]) -> Any:
        """
        A convenience method to format the prompt using a dictionary.
        This provides an API consistent with other components in the framework.
        """
        return self.format(**variables)
    # def invoke(self, variables: Dict[str, Any], **kwargs: Any) -> Any:
    #     return self.format(**variables)
    
    

    def _validate_variables(self, variables: Dict[str, Any]) -> None:
        """
        Internal method to ensure all required variables are provided for formatting.
        Raises a ValueError if any variables are missing.
        """
        missing = set(self.input_variables) - set(variables.keys())
        if missing:
            raise ValueError(f"Missing required input variables: {sorted(list(missing))}")

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(input_variables={self.input_variables})"
