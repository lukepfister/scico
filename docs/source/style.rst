.. _scico_dev_style:


Style Guide
===========

.. raw:: html

    <style type='text/css'>
    div.document ul blockquote {
       margin-bottom: 8px !important;
    }
    div.document li > p {
       margin-bottom: 4px !important;
    }
    div.document li {
      list-style: square outside !important;
      margin-left: 1em !important;
    }
    </style>


Overview
--------

We adhere to `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ with the exception of allowing a line length limit of 99 characters (as opposed to 79 characters), with a stricter limit of 79 characters (as opposed to 72 characters) for docstrings or comments. We use `Black <https://github.com/psf/black>`_ as our PEP-8 Formatter and `isort <https://pypi.org/project/isort/>`_ to sort imports. (Please Set up a `pre-commit hook <https://pre-commit.com>`_ to ensure any modified code passes format check before it is committed to the development repo.)

We aim to incorporate `PEP 526 <https://www.python.org/dev/peps/pep-0484/>`_ type annotations throughout the library.  See the `Mypy <https://mypy.readthedocs.io/en/stable/>`_ type annotation `cheat sheet <https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html>`_ for usage examples. Custom types are defined in :mod:`.typing`.

Our coding conventions are based on both the `numpy conventions <https://numpydoc.readthedocs.io/en/latest/format.html#overview>`_ and the `google docstring conventions <https://google.github.io/styleguide/pyguide.html>`_.

.. todo::

   Briefly explain which components are taken from each convention (see above) to avoid ambiguity in cases in which they differ.

Unicode variable names are allowed for internal usage (e.g. for Greek characters for mathematical symbols), but not as part of the public interface for functions or methods.


Naming
------

Naming conventions for the different programming components are as follows:

.. list-table:: Naming Conventions
   :widths: 20 20
   :header-rows: 1

   * - Component
     - Naming Convention
   * - Modules
     - module_name
   * - Package
     - package_name
   * - Class
     - ClassName
   * - Method
     - method_name
   * - Function
     - function_name
   * - Exception
     - ExceptionName
   * - Variable
     - var_name
   * - Parameter
     - parameter_name
   * - Constant
     - CONSTANT_NAME

These names should be descriptive and unambiguous to avoid confusion within the code and other modules in the future.

Example:

.. code:: Python

    d = 6  # Day of the week == Saturday
    if d < 5:
	print("Weekday")

Here the code could be hard to follow since the name ``d`` is not descriptive and requires extra comments to explain the code, which would have been solved otherwise by good naming conventions.

Example:

.. code:: Python

    fldln = 5 # field length

This could be improved by using the descriptive variable ``field_len``.

Things to avoid:

- Single character names except for the following special cases:

   - Counters or iterators (``i``, ``j``)
   - `e` as an exception identifier (``Exception e``)
   - `f` as a file in ``with`` statements
   - Mathematical notation in which a reference to the paper or algorithm with said notation is preferred if not clear from the intended purpose.

- Trailing underscores unless the component is meant to be protected or private:

   - Protected: Use a single underscore, ``_``, for protected access
   - Pseudo-private: Use double underscores, ``_``, for pseudo-private access via name mangling.

|

Displaying and Printing Strings
-------------------------------

Prefer to use Python f-strings, rather than `.format` or `%` syntax.

.. code:: Python

    state = "active"
    print("The state is %s")        # Not preferred
    print(f"The state is {state}")  # Preferred




Imports
-------

Usage of ``import`` statements should be reserved for packages and modules only and not individual classes or functions. The only exception to this is the typing module.

-  Use ``import x`` for importing packages and modules, where x is the package or module name.
-  Use ``from x import y`` where x is the package name and y is the module name.
-  Use ``from x import y as z`` if two modules named ``y`` are imported or if ``y`` is too long of a name.
-  Use ``import y as z`` when ``z`` is a standard abbreviation like ``import numpy as np``.

|

Variables
---------

Apart from naming conventions there are a few extra documentation and coding practices that can be applied to variables such as:

- Typing Variables:

   - Use a ``: type`` before the function value is assigned

   | Example:

   .. code-block:: python

      a : Foo = SomeDecoratedFunction()

   - Avoid global variables.
   - A function can refer to variables defined in enclosing functions but cannot assign to them.

|

Parameters
----------

There are three important stlyle components for parameters:

- We use type annotations meaning we specify the types of the inputs and outputs of any method.
   - From the ``typing`` module we can use more types such as ``Optional``, ``Union``, and ``Any``.

   | Example:

      .. code-block:: python

	 def foo(a: str) -> str:
	    """Takes an input of type string and returns a value of type string"""
	    ...

- Default Values:

   - Parameter should include ``parameter_name = value`` where value is the default for that particular parameter.
   - If the parameter has a type then the format is ``parameter_name: Type = value``
   - Additionally when documenting parameters, a parameter can only assume one of a fixed set of values, those values can be listed in braces, with the default appearing first.

   | Example:

      .. code-block:: python

	 """
	 letters: {'A', 'B, 'C'}
	     Description of `letters`.
	 """

- NoneType:

   - In Python a ``NoneType`` is a "first-class" type.
   - ``None`` is the most commonly used alias. \* If any of the parameters/arguments can be ``None`` then it has to be declared. ``Optional[T]`` is preferred over ``Union[T, None]``.

   | Example:

      .. code-block:: python

	 def foo(a: Optional[str], b: Optional[Union[str, int]]) -> str:
	    ...

   - For documentation purposes, ``NoneType`` or ``None`` should be written with double backticks

|

Docstrings
----------

Docstrings are a way to document code within Python and it is the first statement within a package, module, class, or function. To generate a document with all the documentation for the code use `pydoc <https://docs.python.org/3/library/pydoc.html>`_.


Typing
~~~~~~

The following are docstring-specific usages that must be explained before going into the creation of said docstrings:

- Always enclose variables in single backticks.
- For the parameter types, be as precise as possible, no need for backticks.


Modules
~~~~~~~

Files must start with a docstring that describes the functionality of the module.

Example:

.. code-block:: python

    """A one-line summary of the module must be terminated by a period.

    Leave a blank line and describe the module or program. Optionally describe exported classes, functions, and/or usage
    examples.

    Usage Example:

    foo = ClassFoo()
    bar = foo.FunctionBar()
    """"

Functions
~~~~~~~~~

| The word *function* encompasses functions, methods, or generators in this section.

The docstring should give enough information to make calls  to the function without needing to read the functions code.

Functions should contain docstrings unless:

- not externally visible (the function name is prefaced with an underscore)
- very short

The docstring should be imperative-style ``"""Fetch rows from a Table"""`` instead of the descriptive-style ``"""Fetches rows from a Table"""``. If the method overrides a method from a base class then it may use a simple docstring referencing that base class such as ``"""See base class"""``, unless the behavior is different from the overridden method or there are extra details that need to be documented.

| There are three sections to function docstrings:

- Args:
    - List each parameter by name, and include a description for each parameter.
- Returns: (or Yield in the case of generators)
    - Describe the type of the return value. If a function only returns None then this section is not required.
- Raises:
   - List all exceptions followed by a description. The name and description should be separated by a colon followed by a space.

Example:

.. code-block:: python

    def fetch_smalltable_rows(table_handle: smalltable.Table,
			      keys: Sequence[Union[bytes, str]],
			      require_all_keys: bool = False,
    ) -> Mapping[bytes, Tuple[str]]:
	"""Fetch rows from a Smalltable.

	Retrieve rows pertaining to the given keys from the Table instance
	represented by table_handle.  String keys will be UTF-8 encoded.

	Args:
	    table_handle:
		An open smalltable.Table instance.
	    keys:
		A sequence of strings representing the key of each table
		row to fetch.  String `keys` will be UTF-8 encoded.
	    require_all_keys: Optional
		If `require_all_keys` is ``True`` only
		rows with values set for all keys will be returned.

	Returns:
	    A dict mapping keys to the corresponding table row data
	    fetched. Each row is represented as a tuple of strings. For
	    example:

	    {b'Serak': ('Rigel VII', 'Preparer'),
	     b'Zim': ('Irk', 'Invader'),
	     b'Lrrr': ('Omicron Persei 8', 'Emperor')}

	    Returned keys are always bytes.  If a key from the keys argument is
	    missing from the dictionary, then that row was not found in the
	    table (and require_all_keys must have been False).

	Raises:
	    IOError: An error occurred accessing the smalltable.
	"""


Classes
~~~~~~~

Classes, like functions, should have a docstring below the definition describing the class and the class functionality. If the class contains public attributes the class should have an attributes section where each attribute is listed by name and followed by a description divided by a colon much like a function's args.

| Example:

.. code:: Python

    class foo:
	"""One liner describing the class.

	Additional information or description for the class.
	Can be multi-line

	Attributes:
	    attr1: First attribute of the class.
	    attr2: Second attribute of the class.
	"""

	def __init__(self):
	    """Should have a docstring of type function."""
	    pass

	def method(self):
	    """Should have a docstring of type: function."""
	    pass


Extra Sections
~~~~~~~~~~~~~~

The following are sections that can be added to functions, modules, classes, or method definitions taken from the numpy style guide.

-  See Also:

   - Refers to related code. Used to direct users to other modules, functions, or classes that they may not be aware of.
   - When referring to functions in the same sub-module, no prefix is needed. Example: For ``numpy.mean`` inside the same sub-module:

	.. code-block:: python

	    """
	    See Also
	    --------
	    average: Weighted average.
	    """

   - For a reference to ``fft`` in another module:

	.. code-block:: python

	   """
	   See Also
	   --------
	   fft.fft2: 2-D fast discrete Fourier transform.
	   """

-  Notes

   -  Provides additional information about the code. May include mathematical equations in LaTeX format:

    | Example:

    .. code-block:: python

	   """
	   Notes
	   -----
	   The FFT is a fast implementation of the discrete Fourier transform:
	       .. math::
		    X(e^{j\omega } ) = x(n)e^{ - j\omega n}
	   """

    | Additionally, math can be used inline:

    .. code-block:: python

	  """
	  Notes
	  -----
	  The value of :math:`\omega` is larger than 5.
	  """

-  Examples:

   -  Uses the doctest format and is meant to showcase usage.
   -  If there are multiple examples include blank lines before and after each example.

    | Example:

    .. code-block:: python

      """
      Examples
      --------
      Necessary imports
      >>> import numpy as np

      Comment explaining example 1.

      >>> np.add(1, 2)
      3

      Comment explaining a new example.

      >>> np.add([1, 2], [3, 4])
      array([4, 6])

      If the example is too long then each line after the first start it
      with a ``...``

      >>> np.add([[1, 2], [3, 4]],
      ...         [[5, 6], [7, 8]]) 
      array([[ 6,  8], 
             [10, 12]])

      """


Comments
~~~~~~~~

There are two types of comments: Block and Inline. A good rule of thumb to follow for when to include a comment in your code is: if you have to explain it or is too hard to figure out at first glance, then comment it. An example of this is complicated operations which most likely require a block of comments beforehand.

.. code-block:: Python

    # We use a block comment because the following code performs a
    # difficult operation. Here we can explain the variables or
    # what the concept of the operation does in an easier
    # to understand way.

    i = i & (i-1) == 0:  # True if i is 0 or a power of 2, explains the concept not the code
