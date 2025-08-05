from tabulicious.formats import (
    Format,
    Plaintext,
    Markdown,
    HTML,
    Atlassian,
    GitHub,
)


__all__ = [
    "Tabulicious",
    "Format",
    "Plaintext",
    "Markdown",
    "HTML",
    "Atlassian",
    "GitHub",
]


class Tabulicious(object):
    _rows: list[list[str]] = None
    _headers: list[str] = None
    _format: Format = None

    def __init__(
        self,
        rows: list[list[str]],
        headers: list[str] = None,
        format: Format = None,
        **kwargs,
    ):
        """Initialise the table with the provided row/column data, optional headers, and
        optional Format subclass reference. Additional arguments will be passed to the
        Format subclass instance according to its supported keyword arguments."""

        # Validate the provided rows argument, ensuring it has the expected type/value
        if not isinstance(rows, list):
            raise TypeError("The 'data' argument must have a list value!")
        else:
            columns: int = None

            for row in rows:
                if not isinstance(row, list):
                    raise TypeError(
                        "The 'rows' argument must reference a list of list values!"
                    )
                else:
                    if columns is None:
                        columns = len(row)
                    elif not len(row) == columns:
                        raise ValueError(
                            "Each row must have the same number of columns!"
                        )

                    for column in row:
                        if column is None:
                            pass
                        elif isinstance(
                            column, (str, int, float, complex, bool)
                        ) or hasattr(column, "__str__"):
                            pass
                        else:
                            raise TypeError(
                                "Each column value must have a string, integer, float or boolean, or custom class that provides a string representation via __str__ method!"
                            )

        self._rows = rows

        # Validate the optional headers argument, ensuring it has the expected type/value
        if headers is None:
            pass
        elif isinstance(headers, list):
            for header in headers:
                if not isinstance(header, str):
                    raise TypeError(
                        "The 'headers' argument must reference a list of string values!"
                    )

            for row in rows:
                if not len(headers) == len(row):
                    raise ValueError(
                        "Each data row must have the same number of columns as the header row!"
                    )
        else:
            raise TypeError(
                "The 'headers' argument, if specified, must have a list value!"
            )

        self._headers = headers

        # Validate the optional format argument, ensuring it has the expected type/value
        if format is None:
            format = Plaintext
        elif issubclass(format, Format) and not format is Format:
            pass
        else:
            raise TypeError(
                "The 'format' argument must reference a Format subclass instance!"
            )

        self._format = format(table=self, **kwargs)

    def __repr__(self) -> str:
        """Return a debugging representation of the class instance."""

        return "<%s(rows: %d, headers: %d, format: %d)}> at %s" % (
            self.__class__.__name__,
            len(self.rows),
            len(self.headers) if self.headers else 0,
            self.format,
            hex(id(self)),
        )

    def __str__(self) -> str:
        """Return a string representation of the table."""

        return self.string()

    @property
    def rows(self) -> list[list[object]]:
        """Return the provided row data for the table."""
        return self._rows

    @property
    def headers(self) -> list[str] | None:
        """Return the provided headers, if any, for the table."""

        return self._headers

    @property
    def columns(self) -> list[list[object]]:
        """Return the provided row data organised into column data."""

        columns: list[list[object]] = []

        for row in self.rows:
            if not len(columns) == len(row):
                for i in range(len(row)):
                    columns.append([])

            for index, column in enumerate(row):
                columns[index].append(column)

        return columns

    @property
    def format(self) -> Format:
        """Return the table Format subclass being used to format the table data."""

        return self._format

    def string(self) -> str:
        """Generate and return the string representation of the table data."""

        return self.format.string()

    def print(self) -> str:
        """Print the string representation of the table data."""

        return self.format.print()


def tabulate(
    rows: list[list[str]],
    headers: list[str] = None,
    format: Format = None,
    **kwargs,
) -> Tabulicious:
    """This helper method supports creating and returning instance of the class."""

    return Tabulicious(
        rows=rows,
        headers=headers,
        format=format,
        **kwargs,
    )
