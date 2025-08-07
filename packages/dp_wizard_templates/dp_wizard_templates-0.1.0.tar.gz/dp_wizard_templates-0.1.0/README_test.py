# pyright: reportUnusedExpression=false
"""
DP Wizard Templates relies on code inspection, so real working examples
need to be in code. This file provides some motivation for the library,
and demonstrates how it can be used idiomatically.

## Motivation

Let's say you want to generate Python code programmatically,
perhaps to demonstrate a workflow with parameters supplied by the user.
One approach would be to use a templating system like Jinja,
but this may be hard to maintain: The template itself is not Python,
so syntax problems will not be obvious until it is filled in.
At the other extreme, constructing code via an AST is very low-level.

DP Wizard Templates is an alternative. The templates are themselves python code,
with the slots to fill in all-caps. This convention means that the template
itself can be parsed as python code, so syntax highlighting and linting still works.
"""

from dp_wizard_templates.code_template import Template


def conditional_print_template(CONDITION, MESSAGE):
    if CONDITION:
        print(MESSAGE)


conditional_print = (
    Template(conditional_print_template)
    .fill_expressions(CONDITION="temp_c < 0")
    .fill_values(MESSAGE="It is freezing!")
    .finish()
)

assert conditional_print == "if temp_c < 0:\n    print('It is freezing!')"

"""
Note the different methods used:
- `fill_expressions()` fills the slot with verbatim text.
  It can be used for an expression like this, or for variable names.
- `fill_values()` fills the slot with the repr of the provided value.
  This might be a string, or it might be a array or dict or other
  data structure, as long as it has a usable repr.
- `finish()` converts the template to a string, and will error
  if not all slots have been filled.

Templates can also be in standalone files. If a string is provided,
the system will prepend '_' and append '.py' and look for a corresponding file.
(The convention of prepending '_' reminds us that although these files
can be parsed, they should not be imported or executed as-is.)
"""

from pathlib import Path

root = Path(__file__).parent / "README_examples"

block_demo = (
    Template("block_demo", root=root)
    .fill_expressions(FUNCTION_NAME="freeze_warning", PARAMS="temp_c")
    .fill_blocks(INNER_BLOCK=conditional_print)
    .finish()
)

assert (
    block_demo
    == '''def freeze_warning(temp_c):
    """
    This demonstrates how larger blocks of code can be built compositionally.
    """
    if temp_c < 0:
        print('It is freezing!')
'''
)

"""
Finally, plain strings can also be used for templates.
"""

assignment = (
    Template("VAR = NAME * 2")
    .fill_expressions(VAR="band")
    .fill_values(NAME="Duran")
    .finish()
)

assert assignment == "band = 'Duran' * 2"

"""
DP Wizard Templates also includes utilities to convert python code
to notebooks, and to convert notebooks to HTML. It is a thin wrapper
which provides default settings for `nbconvert` and `jupytext`.

The python code is converted to a notebook using the jupytext light format:
https://jupytext.readthedocs.io/en/latest/formats-scripts.html#the-light-format
Contiguous comments are coverted to markdown cells,
and contiguous lines of code are converted to code cells.

One additional feature is that a section with a "# Coda" header
will be stripped from notebook output. This allows a notebook
to have produce other artifacts without adding clutter.
"""

from dp_wizard_templates.converters import convert_py_to_nb, convert_nb_to_html


def notebook_template(TITLE, BLOCK, FUNCTION_NAME):
    # # TITLE
    #
    # Comments will be rendered as *Markdown*.
    # The + and - below ensure that only one cell is produced,
    # even though the lines are not contiguous

    # +
    BLOCK

    FUNCTION_NAME(-10)
    # -

    # # Coda
    #
    # Extra computations that will not be rendered.

    2 + 2


title = "Hello World!"
notebook_py = (
    Template(notebook_template)
    .fill_blocks(BLOCK=block_demo)
    .fill_expressions(FUNCTION_NAME="freeze_warning", TITLE=title)
    .finish()
)

notebook_ipynb = convert_py_to_nb(notebook_py, title=title, execute=True)
(root / "hello-world.ipynb").write_text(notebook_ipynb)

notebook_html = convert_nb_to_html(notebook_ipynb)
(root / "hello-world.html").write_text(notebook_html)
