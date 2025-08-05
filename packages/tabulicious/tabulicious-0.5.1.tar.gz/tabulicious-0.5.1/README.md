# Tabulicious

The Tabulicious library provides functionality to generate simple text-based formatted
tables for command line and documentation use in a range of formats including plaintext,
Markdown and HTML.

### Requirements

The Tabulicious library has been tested to work with Python 3.10, 3.11, 3.12 and 3.13,
but has not been tested, nor is its use supported with earlier versions of Python.

### Installation

The library is available from the PyPI repository, so may be added easily to a project's
dependencies via its `requirements.txt` file or similar by referencing the library's
name, `tabulicious`, or the library may be installed directly onto your local development
system using `pip install` by entering the following command:

	$ pip install tabulicious

### Introduction

The Tabulicious library can be used to easily create text-based tables in a range of
formats from a list of row data, where each row has the same number of columns, and each
column contains a printable value or a `None` value. Printable values include all values
that have a string representation, which include all of the built-in and custom types
that support the `__str__` method.

Instances of the library can be created by creating an instance of the `Tabulicious`
class, or by using the `tabulate` helper function, both of which can be imported from
the top-level `tabulicious` module.

### Examples of Use

```python
from tabulicious import Tabulicious

# All rows must have the same number of columns, even if a column in a given row is
# empty, a value must still be supplied for that column, as an empty string or `None`:
rows = [
    ["Column 1A", "Column 1B", "Column 1C"],
    ["Column 2A", None, "Column 2C"],
]

# Table headers are optional, but if supplied, must have the same number of columns as
# the row data does:
headers = ["Header 1", "Header 2", "Header 3"]

# Create a new instance of the class with the row data and optional headers
table = Tabulicious(rows=rows, headers=headers)

# The Tabulicious class provides a string representation of itself whenever its __str__ 
# method is called, so can be passed to methods like `print` or concatenated with other
# string output:
print(table)
```

The above code sample generates the following output:

```text
┌───────────┬───────────┬───────────┐
│ Header 1  │ Header 2  │ Header 3  │
├───────────┼───────────┼───────────┤
│ Column 1A │ Column 1B │ Column 1C │
├───────────┼───────────┼───────────┤
│ Column 2A │           │ Column 2C │
└───────────┴───────────┴───────────┘
```

The library also provides a `tabulate` helper method that takes the same arguments as
the `Tabulicious` class:

```python
from tabulicious import tabulate

# All rows must have the same number of columns, even if a column in a given row is
# empty, a value must still be supplied for that column, as an empty string or `None`:
rows = [
    ["Column 1A", "Column 1B", "Column 1C"],
    ["Column 2A", None, "Column 2C"],
]

# Table headers are optional, but if supplied, must have the same number of columns as
# the row data does:
headers = ["Header 1", "Header 2", "Header 3"]

# Create a new instance of the class with the row data and optional headers
table = tabulate(rows=rows, headers=headers)

# The Tabulicious class provides a string representation of itself whenever its __str__ 
# method is called, so can be passed to methods like `print` or concatenated with other
# string output:
print(table)
```

### Formatting

Support for the various output formats are provided through the collection of `Format`
subclasses provided by the library. These subclasses are responsible for formatting the
tabular row and optional header data and formatting it into the chosen text-based format
such as Markdown, HTML or plaintext.

By default the library generates plaintext formatted tables using the `Plaintext` format
subclass. As the `Plaintext` formatter is the default, it does not need to be specified
when creating a plaintext formatted table. To use one of the other formatter subclasses,
import the desired formatter from the library and pass it to the class initialiser using
the `format` keyword argument. The list of currently supported formatters are listed in
the [**Formatters**](#formatters) section below.

For example, to generate Markdown formatted tables, import the `Markdown` subclass from
the library and pass it to the initialiser using the `format` keyword argument as shown
below:

```python
from tabulicious import tabulate, Markdown

# All rows must have the same number of columns, even if a column in a given row is
# empty, a value must still be supplied for that column, as an empty string or `None`:
rows = [
    ["Column 1A", "Column 1B", "Column 1C"],
    ["Column 2A", None, "Column 2C"],
]

# Table headers are optional, but if supplied, must have the same number of columns as
# the row data does:
headers = ["Header 1", "Header 2", "Header 3"]

# Create a new instance of the class with the row data and optional headers; the same
# arguments can be passed to the Tabulicious class directly:
table = tabulate(rows=rows, headers=headers, format=Markdown)

print(table)
```

The above code sample generates the following output:

```text
| Header 1 | Header 2 | Header 3 |
| :-- | :-- | :-- |
| Column 1A | Column 1B | Column 1C |
| Column 2A | Column 2B | Column 2C |
```

Which when rendered as Markdown, will look like the following:

| Header 1 | Header 2 | Header 3 |
| :-- | :-- | :-- |
| Column 1A | Column 1B | Column 1C |
| Column 2A | Column 2B | Column 2C |

To generate HTML formatted tables, import the `HTML` subclass from the library and pass
it to the initialiser using the `format` keyword argument as shown below:

```python
from tabulicious import Tabulicious, HTML

# All rows must have the same number of columns, even if a column in a given row is
# empty, a value must still be supplied for that column, as an empty string or `None`:
rows = [
    ["Column 1A", "Column 1B", "Column 1C"],
    ["Column 2A", None, "Column 2C"],
]

# Table headers are optional, but if supplied, must have the same number of columns as
# the row data does:
headers = ["Header 1", "Header 2", "Header 3"]

# Create a new instance of the class with the row data and optional headers; the same
# arguments can be passed to the tabulate function:
table = Tabulicious(rows=rows, headers=headers, format=HTML)

print(table)
```

The above code sample generates the following output:

```text
<table>
  <thead>
    <tr>
      <td>Header 1</td><td>Header 2</td><td>Header 3</td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Column 1A</td><td>Column 1B</td><td>Column 1C</td>
    </tr>
    <tr>
      <td>Column 2A</td><td>Column 2B</td><td>Column 2C</td>
    </tr>
  </tbody>
</table>
```

Which when rendered as HTML, will look like the following:

<table>
  <thead>
    <tr>
      <td>Header 1</td><td>Header 2</td><td>Header 3</td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Column 1A</td><td>Column 1B</td><td>Column 1C</td>
    </tr>
    <tr>
      <td>Column 2A</td><td>Column 2B</td><td>Column 2C</td>
    </tr>
  </tbody>
</table>

<a name='formatters'></a>
### Formatters

The Tabulicious library currently provides the following formatter subclasses which can]
be used to generate text-based tables of the relevant format:

| Formatter   | Format                     | Notes                                    |
| :---------- | :------------------------- | :--------------------------------------- |
| `Plaintext` | Plaintext formatted tables | The `Plaintext` formatter is the default |
| `Markdown`  | Markdown formatted tables  |                                          |
| `HTML`      | HTML formatted tables      |                                          |
| `Atlassian` | Atlassian formatted tables | For Jira tickets, Confluence pages, etc  |

#### Plaintext Formatter

The Plaintext formatter offers the following configuration options:

 * style (control over the border and header styling)
 * minimum column width (number of characters)
 * maximum column width (number of characters)
 * fixed column widths (number of characters)
 * column alignments

The Plaintext formatter offers the following styles:

| Style  | Description                                                              |
| :----- | :----------------------------------------------------------------------- |
| Simple | The `simple` style uses standard ASCII characters to form the table.     |
| Single | The `single` style uses single box drawing characters to form the table. |
| Double | The `double` style uses double box drawing characters to form the table. |
| Curved | The `curved` style uses curved box drawing characters to form the table. |
| Bolded | The `bolded` style uses bolded box drawing characters to form the table. |

#### Plaintext Formatter: Examples

The `simple` style will generate tables similar to the following with ASCII borders:

```text
+-----------+-----------+-----------+
| Header 1  | Header 2  | Header 3  |
+-----------+-----------+-----------+
| Column 1A | Column 1B | Column 1C |
+-----------+-----------+-----------+
| Column 2A | Column 2B | Column 2C |
+-----------+-----------+-----------+
```

The `single` style will generate tables similar to the following with single borders:

```text
┌───────────┬───────────┬───────────┐
│ Header 1  │ Header 2  │ Header 3  │
├───────────┼───────────┼───────────┤
│ Column 1A │ Column 1B │ Column 1C │
├───────────┼───────────┼───────────┤
│ Column 2A │ Column 2B │ Column 2C │
└───────────┴───────────┴───────────┘
```

The `double` style will generate tables similar to the following with double borders:

```text
╔═══════════╦═══════════╦═══════════╗
║ Header 1  ║ Header 2  ║ Header 3  ║
╠═══════════╬═══════════╬═══════════╣
║ Column 1A ║ Column 1B ║ Column 1C ║
╠═══════════╬═══════════╬═══════════╣
║ Column 2A ║ Column 2B ║ Column 2C ║
╚═══════════╩═══════════╩═══════════╝
```

The `bolded` style will generate tables similar to the following with bold borders:

```text
┏━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Header 1  ┃ Header 2  ┃ Header 3  ┃
┣━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━┫
┃ Column 1A ┃ Column 1B ┃ Column 1C ┃
┣━━━━━━━━━━━╋━━━━━━━━━━━╋━━━━━━━━━━━┫
┃ Column 2A ┃ Column 2B ┃ Column 2C ┃
┗━━━━━━━━━━━┻━━━━━━━━━━━┻━━━━━━━━━━━┛
```

The `curved` style will generate tables similar to the following with curved borders:

```text
╭───────────┬───────────┬───────────╮
│ Header 1  │ Header 2  │ Header 3  │
├───────────┼───────────┼───────────┤
│ Column 1A │ Column 1B │ Column 1C │
├───────────┼───────────┼───────────┤
│ Column 2A │ Column 2B │ Column 2C │
╰───────────┴───────────┴───────────╯
```

#### Markdown Formatter

The Markdown formatter offers the following configuration options:

 * column alignments

#### HTML Formatter

The HTML formatter offers the following configuration options:

 * column alignments

#### Atlassian Formatter: Examples

The `Atlassian` subclass will generate tables similar to the following:

```text
|| Header 1 || Header 2 || Header 3 ||
| Column 1A | Column 1B | Column 1C |
| Column 2A | Column 2B | Column 2C |
```

### Copyright & License Information

Copyright © 2025 Daniel Sissman; licensed under the MIT License.