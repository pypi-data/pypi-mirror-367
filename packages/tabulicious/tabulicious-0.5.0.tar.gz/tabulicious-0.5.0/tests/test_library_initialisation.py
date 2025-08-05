from tabulicious import (
    Tabulicious,
    tabulate,
)


def test_initialisation_class(
    headers: list[str], rows: list[list[object]], data: callable
):
    table = Tabulicious(
        headers=headers,
        rows=rows,
    )

    assert isinstance(table, Tabulicious)
    assert table.headers == headers
    assert table.rows == rows

    assert str(table) == data("examples/plaintext/default.txt")


def test_initialisation_function(
    headers: list[str], rows: list[list[object]], data: callable
):
    table = tabulate(
        headers=headers,
        rows=rows,
    )

    assert isinstance(table, Tabulicious)
    assert table.headers == headers
    assert table.rows == rows

    assert str(table) == data("examples/plaintext/default.txt")


def test_initialisation_values(
    headers: list[str], rows: list[list[object]], data: callable
):
    table = Tabulicious(
        headers=headers,
        rows=rows,
    )

    assert isinstance(table, Tabulicious)

    assert table.headers == headers

    assert table.rows == rows

    assert len(table.headers) == len(table.columns)

    assert str(table) == data("examples/plaintext/default.txt")
