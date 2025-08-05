from tabulicious.formats import Format


class Markdown(Format):
    """The Markdown subclass generates tables using for use in Markdown documents and
    other representations that support Markdown formatted text, including standard
    Markdown formatted tables."""

    _alignments: list[str] = None
    _column_name: str = None

    def __init__(self, column_name: str = None, alignments: list[str] = None, **kwargs):
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

    @property
    def alignments(self) -> list[str] | None:
        return self._alignments

    def string(self) -> str:
        """Generates a Markdown formatted table similar to the following:

        | Header 1 | Header 2 | Header 3 |
        | :------- | :------: | -------: |
        | Data 1A  | Data 2A  | Data 3A  |
        | Data 1B  | Data 2B  | Data 3B  |
        """

        string: str = ""

        # Table Headers
        if self.table.headers:
            string += "|"
            for header in self.table.headers:
                string += f" {header} |"
            string += "\n"
        else:
            string += "|"
            for index, column in enumerate(self.table.columns, start=1):
                string += f" {self._column_name} {index} |"
            string += "\n"

        # Header Separator/Alignment Markers
        string += "|"
        for index, column in enumerate(self.table.columns):
            if self.alignments and len(self.alignments) > index:
                if self.alignments[index] == "left":
                    string += " :-- |"
                elif self.alignments[index] == "center":
                    string += " :-: |"
                elif self.alignments[index] == "right":
                    string += " --: |"
                else:  # default to left alignment
                    string += " :-- |"
            else:  # default to left alignment
                string += " :-- |"
        string += "\n"

        # Table Row Columns
        for row in self.table.rows:
            string += "|"
            for column in row:
                string += " " + str(column) + " |"
            string += "\n"

        return string

    def print(self):
        print(self.string())
