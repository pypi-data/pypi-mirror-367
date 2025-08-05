from tabulicious import (
    Tabulicious,
    Atlassian,
)


def test_table_atlassian(headers: list[str], rows: list[list[object]], data: callable):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Atlassian,
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/atlassian/example.txt")
