from tabulicious.formats import Format

import math


class Plaintext(Format):
    """The Plaintext subclass generates tables using for use in plaintext cases where a
    monospaced font can be used such as documentation and the command line."""

    _styles: dict[str, dict[str, str]] = {
        "single": {
            "tl": "┌",
            "ml": "├",
            "bl": "└",
            "tm": "┬",
            "mm": "┼",
            "bm": "┴",
            "tr": "┐",
            "mr": "┤",
            "br": "┘",
            "hr": "─",
            "vr": "│",
        },
        "double": {
            "tl": "╔",
            "ml": "╠",
            "bl": "╚",
            "tm": "╦",
            "mm": "╬",
            "bm": "╩",
            "tr": "╗",
            "mr": "╣",
            "br": "╝",
            "hr": "═",
            "vr": "║",
        },
        "bolded": {
            "tl": "┏",
            "ml": "┣",
            "bl": "┗",
            "tm": "┳",
            "mm": "╋",
            "bm": "┻",
            "tr": "┓",
            "mr": "┫",
            "br": "┛",
            "hr": "━",
            "vr": "┃",
        },
        "curved": {
            "tl": "╭",
            "ml": "├",
            "bl": "╰",
            "tm": "┬",
            "mm": "┼",
            "bm": "┴",
            "tr": "╮",
            "mr": "┤",
            "br": "╯",
            "hr": "─",
            "vr": "│",
        },
        "simple": {
            "tl": "+",
            "ml": "+",
            "bl": "+",
            "tm": "+",
            "mm": "+",
            "bm": "+",
            "tr": "+",
            "mr": "+",
            "br": "+",
            "hr": "-",
            "vr": "|",
        },
    }
    _style: str = None
    _widths: list[int] = None
    _alignments: list[str] = None
    _bolding: bool = False

    def __init__(
        self,
        alignments: list[str] = None,
        style: str = None,
        bolding: bool = False,
        min_width: int = None,
        max_width: int = None,
        widths: list[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if style is None:
            style = "single"
        elif isinstance(style, str):
            if style in self._styles:
                pass
            else:
                raise ValueError(
                    f"The 'style' argument, if set, must have one of the following values: {', '.join(list(self._styles.keys()))}!"
                )
        else:
            raise TypeError("The 'style' argument, if set, must have a string value!")

        self._style = style

        if min_width is None:
            min_width = 0
        elif isinstance(min_width, int):
            if min_width > 0:
                self._min_width = min_width
            else:
                raise ValueError(
                    "The 'min_width' argument must have a positive integer value!"
                )
        else:
            raise TypeError("The 'min_width' argument must have an integer value!")

        if max_width is None:
            max_width = 0
        elif isinstance(max_width, int):
            if max_width > 0:
                self._max_width = max_width
            else:
                raise ValueError(
                    "The 'max_width' argument must have a positive integer value!"
                )
        else:
            raise TypeError("The 'max_width' argument must have an integer value!")

        self._widths: list[int] = []

        if isinstance(self.table.headers, list):
            for header in self.table.headers:
                self._widths.append(len(header))

        for row in self.table.rows:
            if isinstance(self.table.headers, list) and not len(
                self.table.headers
            ) == len(row):
                raise RuntimeError(
                    "The number of columns must match the number of header columns!"
                )

            for index, column in enumerate(row):
                value = str(column)

                if (width := len(value)) >= 0:
                    if min_width > 0 and width < min_width:
                        width = min_width

                    if max_width > 0 and width > max_width:
                        width = max_width + 1  # +1 for the ellipse

                    if isinstance(widths, list) and len(widths) > index:
                        if not isinstance(widths[index], int):
                            raise TypeError(
                                "Each column width, if specified, must have an integer value!"
                            )
                        elif widths[index] > 0 and width > widths[index]:
                            width = widths[index]
                        elif widths[index] > 0 and width < widths[index]:
                            width = widths[index]

                    if len(self._widths) > index:
                        if width > self._widths[index]:
                            self._widths[index] = width
                        elif width < self._widths[index]:
                            pass
                    else:
                        self._widths.append(width)

        coltypes: list[set[type]] = [set() for i in range(len(self._widths))]

        for row in self.table.rows:
            for index, column in enumerate(row):
                coltypes[index].add(type(column))

        self._alignments: list[str] = []

        for coltype in coltypes:
            if len(coltype) == 1:
                if issubclass(
                    typed := coltype.pop(), (int, float, complex)
                ) and not issubclass(typed, bool):
                    self._alignments.append("right")
                else:
                    self._alignments.append("left")
            else:
                self._alignments.append("left")

        if alignments is None:
            pass
        elif isinstance(alignments, list):
            if len(alignments) >= len(self.table.columns):
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

        if isinstance(bolding, bool):
            self._bolding = bolding
        else:
            raise TypeError(
                "The 'bolding' argument, if specified, must have a boolean value!"
            )

    def _characters(self) -> dict[str, str]:
        """Return the character set used to draw the table borders for the selected style."""

        return self._styles[self._style]

    def _separator(self, position: str, separator: str = None):
        # Get the character set used to draw the table borders for the selected style
        characters: dict[str, str] = self._characters()

        if separator is None:
            separator = characters["hr"]

        table = ""

        if position == "top":
            table += characters["tl"]  # "╔"
        elif position == "header" or position == "middle":
            table += characters["ml"]  # "╠"
        elif position == "bottom":
            table += characters["bl"]  # "╚"

        count: int = len(self._widths)
        for index, width in enumerate(self._widths, start=1):
            table += separator * (width + 2)
            if index < count:
                if position == "top":
                    table += characters["tm"]  # "╦"
                elif position == "header" or position == "middle":
                    table += characters["mm"]  # "╬"
                elif position == "bottom":
                    table += characters["bm"]  # "╩"

        if position == "top":
            table += characters["tr"]  # "╗"
        elif position == "header" or position == "middle":
            table += characters["mr"]  # "╣"
        elif position == "bottom":
            table += characters["br"]  # "╝"

        return table

    def _row(self, row: list[str], header: bool = False):
        # Get the character set used to draw the table borders for the selected style
        characters: dict[str, str] = self._characters()

        table = characters["vr"]  # "║"

        def font(value: str) -> str:
            if header is True:
                if self._bolding is True:
                    return f"\033[1m{value}\033[0m"
                else:
                    return value
            elif header is False:
                return value

        for index, column in enumerate(row):
            table += " "

            if column is None:
                value = ""
                length = 0
            else:
                value = str(column)
                length = len(value)
                value = font(value)

            if self._alignments[index] == "right":
                if length < self._widths[index]:
                    table += " " * (self._widths[index] - length)
                    table += value
                elif length > self._widths[index]:
                    table += value[0 : (self._widths[index] - 1)] + "…"
                else:
                    table += value
            elif self._alignments[index] == "center":
                if length < self._widths[index]:
                    lendiff = self._widths[index] - length
                    lenhalf = math.ceil(lendiff / 2)
                    table += " " * lenhalf
                    table += value

                    if (lenhalf + length + lenhalf) > self._widths[index]:
                        lenhalf = lenhalf - (
                            (lenhalf + length + lenhalf) - self._widths[index]
                        )

                    table += " " * lenhalf
                elif length > self._widths[index]:
                    table += value[0 : (self._widths[index] - 1)] + "…"
                else:
                    table += value
            else:
                if length < self._widths[index]:
                    table += value
                    table += " " * (self._widths[index] - length)
                elif length > self._widths[index]:
                    table += value[0 : (self._widths[index] - 1)] + "…"
                else:
                    table += value

            table += " "
            table += characters["vr"]  # "║"

        return table

    def string(self) -> str:
        """Generates a plain text formatted table similar to the following:

        ┌───────────┬───────────┬───────────┐
        │ Header 1  │ Header 2  │ Header 3  │
        ├───────────┼───────────┼───────────┤
        │ Column 1A │ Column 1B │ Column 1C │
        ├───────────┼───────────┼───────────┤
        │ Column 2A │ Column 2B │ Column 2C │
        └───────────┴───────────┴───────────┘
        """

        # Get the character set used to draw the table borders for the selected style
        characters: dict[str, str] = self._characters()

        # Table Top Border/Separator
        string: str = self._separator("top") + "\n"

        count: int = len(self.table.rows)

        # Table Header Row & Row Separator
        if isinstance(self.table.headers, list) and len(self.table.headers) > 0:
            string += self._row(self.table.headers, header=True) + "\n"

            if count > 0:
                string += self._separator("header", characters["hr"]) + "\n"
            else:
                string += self._separator("bottom", characters["hr"]) + "\n"

        # Table Row Columns & Row Separator
        for index, row in enumerate(self.table.rows, start=1):
            string += self._row(row) + "\n"
            string += self._separator("middle" if index < count else "bottom") + "\n"

        return string

    def print(self):
        """Print the string representation of the table."""

        print(self.string())
