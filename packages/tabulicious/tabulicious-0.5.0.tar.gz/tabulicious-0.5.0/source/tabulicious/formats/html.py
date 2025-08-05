from tabulicious.formats import Format


class HTML(Format):
    """The HTML subclass generates tables using for use in HTML documents and other
    representations that support HTML formatted text."""

    _alignments: list[str] = None
    _column_name: str = None
    _indent: int | bool = False

    def __init__(
        self,
        column_name: str = None,
        alignments: list[str] = None,
        indent: int | bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if column_name is None:
            self._column_name = "Column"
        elif isinstance(column_name, str):
            self._column_name = column_name
        else:
            raise TypeError(
                "The 'column_name' argument, if specified, must havea a string value!"
            )

        if alignments is None:
            pass
        elif isinstance(alignments, list):
            if len(alignments) == len(self.table.columns):
                self._alignments: list[str] = []

                for alignment in alignments:
                    if isinstance(alignment, str):
                        if alignment in ["left", "center", "right"]:
                            self._alignments.append(alignment)
                        else:
                            raise ValueError(
                                "Each alignment value must be one of: 'left', 'center', 'right'!"
                            )
                    else:
                        raise TypeError(
                            "Each alignment value must have a string value!"
                        )
            else:
                raise ValueError(
                    "The 'alignments' argument must have the same number of items as there are columns of data!"
                )
        else:
            raise TypeError("The 'alignments' argument must have a list value!")

        if isinstance(indent, bool):
            self._indent = indent
        elif isinstance(indent, int):
            if indent >= 1:
                self._indent = indent
            else:
                raise ValueError(
                    "The 'indent' argument, if specified, must have a positive integer value, starting at 1!"
                )
        else:
            raise TypeError(
                "The 'indent' argument, if specified, must have an integer or boolean value!"
            )

    @property
    def alignments(self) -> list[str] | None:
        return self._alignments

    def _alignment(self, index: int) -> str:
        alignment: str = ""

        if self.alignments and len(self.alignments) > index:
            alignment = f" align='{self.alignments[index]}'"

        return alignment

    def _indenter(self, string: str, level: int) -> str:
        if isinstance(self.indent, bool):
            if self.indent is True:
                string = ("\t" * level) + string + "\n"
        elif isinstance(self.indent, int) and self.indent > 0:
            string = ((" " * level) * self.indent) + string + "\n"

        return string

    @property
    def indent(self) -> int | bool:
        return self._indent

    def string(self) -> str:
        """Generates a HTML formatted table similar to the following:

        <table>
            <thead>
                <tr>
                    <td align='left'>Header 1</td>
                    <td align='center'>Header 2</td>
                    <td align='right'>Header 3</td>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td align='left'>Column 1A</td>
                    <td align='center'>Column 1B</td>
                    <td align='right'>Column 1C</td>
                </tr>
                <tr>
                    <td align='left'>Column 2A</td>
                    <td align='center'>Column 2B</td>
                    <td align='right'>Column 2C</td>
                </tr>
            </tbody>
        </table>
        """

        # Opening Table Tag
        string: str = self._indenter("<table>", 0)

        # Table Headers
        if self.table.headers:
            string += self._indenter("<thead>", 1)
            string += self._indenter("<tr>", 2)
            for index, header in enumerate(self.table.headers):
                align = self._alignment(index)
                string += self._indenter(f"<td{align}>{header}</td>", 3)
            string += self._indenter("</tr>", 2)
            string += self._indenter("</thead>", 1)
        else:
            string += self._indenter("<thead>", 1)
            string += self._indenter("<tr>", 2)
            for index, column in enumerate(self.table.columns):
                align = self._alignment(index)
                string += self._indenter(
                    f"<td{align}>{self._column_name} {index + 1}</td>", 3
                )
            string += self._indenter("</tr>", 2)
            string += self._indenter("</thead>", 1)

        # Table Body Row Columns
        string += self._indenter("<tbody>", 1)
        for row in self.table.rows:
            string += self._indenter("<tr>", 2)
            for index, column in enumerate(row):
                align = self._alignment(index)
                string += self._indenter(f"<td{align}>" + str(column) + "</td>", 3)
            string += self._indenter("</tr>", 2)
        string += self._indenter("</tbody>", 1)

        # Closing Table Tag
        string += self._indenter("</table>", 0)

        return string

    def print(self):
        print(self.string())
