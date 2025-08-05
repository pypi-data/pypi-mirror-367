from tabulicious import (
    Tabulicious,
    GitHub,
)


def test_table_github(headers: list[str], rows: list[list[object]], data: callable):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=GitHub,
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/github/example.md")
