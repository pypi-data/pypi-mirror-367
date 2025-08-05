from tabulicious.formats import Format


class Atlassian(Format):
    """The Atlassian subclass generates tables using for use in Jira tickets and other
    representations that support Atlassian formatted tables, like Confluence pages."""

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

    def string(self) -> str:
        """Generates a Atlassian formatted table similar to the following:

        || Header 1 || Header 2 || Header 3 ||
        | Data 1A  | Data 2A  | Data 3A  |
        | Data 1B  | Data 2B  | Data 3B  |
        """

        string: str = ""

        # Table Headers
        if self.table.headers:
            string += "||"
            for header in self.table.headers:
                string += f" {header} ||"
            string += "\n"
        else:
            string += "||"
            for index, column in enumerate(self.table.columns, start=1):
                string += f" {self._column_name} {index} ||"
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
