from tabulicious import (
    Tabulicious,
    HTML,
)


def test_table_html(headers: list[str], rows: list[list[object]], data: callable):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=HTML,
        indent=2,
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/html/example.html")
