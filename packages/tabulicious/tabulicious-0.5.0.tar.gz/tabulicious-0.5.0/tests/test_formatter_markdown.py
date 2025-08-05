from tabulicious import (
    Tabulicious,
    Markdown,
)


def test_table_markdown(headers: list[str], rows: list[list[object]], data: callable):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Markdown,
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/markdown/example.md")
