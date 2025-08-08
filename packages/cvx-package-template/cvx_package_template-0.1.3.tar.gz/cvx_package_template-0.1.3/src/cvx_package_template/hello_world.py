"""Hello World module demonstrating numpy-style docstrings.

This module provides example functions and classes with comprehensive
numpy-style docstrings for documentation generation.

Examples
--------
>>> from cvx_package_template.hello_world import hello_world, Calculator
>>> hello_world()
'Hello, World!'
>>> calc = Calculator(10)
>>> calc.add(5)
15.0

"""

import numpy as np


def hello_world(name: str | None = None, count: int = 1) -> str:
    """Generate a greeting message.

    This function creates a customizable greeting message that can
    be personalized with a name and repeated multiple times.

    Parameters
    ----------
    name : str, optional
        The name to include in the greeting. If None, uses "World".
        Default is None.
    count : int, optional
        Number of times to repeat the greeting. Must be positive.
        Default is 1.

    Returns
    -------
    str
        The formatted greeting message. If count > 1, greetings are
        separated by newlines.

    Raises
    ------
    ValueError
        If count is not a positive integer.
    TypeError
        If name is not a string or None.

    Examples
    --------
    >>> hello_world()
    'Hello, World!'

    >>> hello_world("Alice")
    'Hello, Alice!'

    >>> result = hello_world("Bob", count=2)
    >>> print(result)
    Hello, Bob!
    Hello, Bob!

    Notes
    -----
    This function demonstrates proper numpy-style docstring formatting
    for API documentation generation.

    See Also
    --------
    Calculator.greet : Another greeting method in this module

    """
    if count <= 0:
        msg = "count must be a positive integer"
        raise ValueError(msg)

    if name is not None and not isinstance(name, str):
        msg = "name must be a string or None"
        raise TypeError(msg)

    target = name if name is not None else "World"
    greeting = f"Hello, {target}!"

    if count == 1:
        return greeting

    return "\n".join([greeting] * count)


def calculate_statistics(data: list[int | float]) -> dict[str, float]:
    """Calculate basic statistics for a list of numbers.

    Computes mean, median, standard deviation, minimum, and maximum
    values for the input data.

    Parameters
    ----------
    data : list of int or float
        Input data for statistical analysis. Must contain at least one
        numeric value.

    Returns
    -------
    dict
        Dictionary containing the following statistics:

        - 'mean' : float
            Arithmetic mean of the data
        - 'median' : float
            Median value of the data
        - 'std' : float
            Standard deviation of the data
        - 'min' : float
            Minimum value in the data
        - 'max' : float
            Maximum value in the data

    Raises
    ------
    ValueError
        If data is empty or contains non-numeric values.
    TypeError
        If data is not a list.

    Examples
    --------
    >>> data = [1, 2, 3, 4, 5]
    >>> stats = calculate_statistics(data)
    >>> stats['mean']
    3.0
    >>> stats['median']
    3.0

    Notes
    -----
    This function uses numpy for numerical computations when available,
    falling back to built-in functions otherwise.

    """
    if not isinstance(data, list):
        msg = "data must be a list"
        raise TypeError(msg)

    if not data:
        msg = "data cannot be empty"
        raise ValueError(msg)

    if not all(isinstance(x, (int, float)) for x in data):
        msg = "data must contain only numeric values"
        raise ValueError(msg)

    arr = np.array(data)

    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }


class Calculator:
    """A simple calculator class demonstrating numpy-style docstrings.

    This class provides basic arithmetic operations and maintains a running
    total that can be manipulated through various methods.

    Parameters
    ----------
    initial_value : int or float, optional
        The starting value for the calculator. Default is 0.

    Attributes
    ----------
    value : float
        The current value stored in the calculator.
    history : list of str
        A history of operations performed on the calculator.

    Examples
    --------
    >>> calc = Calculator(10)
    >>> calc.add(5)
    15.0
    >>> calc.multiply(2)
    30.0
    >>> calc.get_history()
    ['Initialized with 10', 'Added 5', 'Multiplied by 2']

    Notes
    -----
    All arithmetic operations modify the internal state and return
    the new value for convenience.

    """

    def __init__(self, initial_value: float = 0) -> None:
        """Initialize the calculator with a starting value.

        Parameters
        ----------
        initial_value : int or float, optional
            The starting value for the calculator. Default is 0.

        Raises
        ------
        TypeError
            If initial_value is not a number.

        """
        if not isinstance(initial_value, (int, float)):
            msg = "initial_value must be a number"
            raise TypeError(msg)

        self.value: float = float(initial_value)
        self.history: list[str] = [f"Initialized with {initial_value}"]

    def add(self, x: float) -> float:
        """Add a value to the current calculator value.

        Parameters
        ----------
        x : int or float
            The value to add.

        Returns
        -------
        float
            The new calculator value after addition.

        Raises
        ------
        TypeError
            If x is not a number.

        Examples
        --------
        >>> calc = Calculator(10)
        >>> calc.add(5)
        15.0

        """
        if not isinstance(x, (int, float)):
            msg = "x must be a number"
            raise TypeError(msg)

        self.value += x
        self.history.append(f"Added {x}")
        return self.value

    def multiply(self, x: float) -> float:
        """Multiply the current calculator value by a factor.

        Parameters
        ----------
        x : int or float
            The factor to multiply by.

        Returns
        -------
        float
            The new calculator value after multiplication.

        Raises
        ------
        TypeError
            If x is not a number.

        Examples
        --------
        >>> calc = Calculator(10)
        >>> calc.multiply(3)
        30.0

        """
        if not isinstance(x, (int, float)):
            msg = "x must be a number"
            raise TypeError(msg)

        self.value *= x
        self.history.append(f"Multiplied by {x}")
        return self.value

    def reset(self, new_value: float = 0) -> float:
        """Reset the calculator to a new value.

        Parameters
        ----------
        new_value : int or float, optional
            The value to reset to. Default is 0.

        Returns
        -------
        float
            The new calculator value.

        Raises
        ------
        TypeError
            If new_value is not a number.

        Examples
        --------
        >>> calc = Calculator(10)
        >>> calc.add(5)
        15.0
        >>> calc.reset()
        0.0

        """
        if not isinstance(new_value, (int, float)):
            msg = "new_value must be a number"
            raise TypeError(msg)

        self.value = float(new_value)
        self.history.append(f"Reset to {new_value}")
        return self.value

    def get_history(self) -> list[str]:
        """Get the operation history.

        Returns
        -------
        list of str
            A list of strings describing each operation performed.

        Examples
        --------
        >>> calc = Calculator(5)
        >>> calc.add(3)
        8.0
        >>> calc.get_history()
        ['Initialized with 5', 'Added 3']

        """
        return self.history.copy()

    def greet(self, name: str = "Calculator") -> str:
        """Generate a greeting from the calculator.

        Parameters
        ----------
        name : str, optional
            The name to greet. Default is "Calculator".

        Returns
        -------
        str
            A greeting message including the current calculator value.

        Examples
        --------
        >>> calc = Calculator(42)
        >>> calc.greet("Alice")
        'Hello Alice! My current value is 42.0'

        """
        return f"Hello {name}! My current value is {self.value}"
