from tabulicious import (
    Tabulicious,
    Plaintext,
)


def test_table_plaintext_default(
    headers: list[str], rows: list[list[object]], data: callable
):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Plaintext,  # this the the default so does not need to be specified
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/plaintext/default.txt")


def test_table_plaintext_single(
    headers: list[str], rows: list[list[object]], data: callable
):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Plaintext,  # this the the default so does not need to be specified
        style="single",  # this is the default style
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/plaintext/single.txt")


def test_table_plaintext_bolded(
    headers: list[str], rows: list[list[object]], data: callable
):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Plaintext,  # this the the default so does not need to be specified
        style="bolded",
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/plaintext/bolded.txt")


def test_table_plaintext_curved(
    headers: list[str], rows: list[list[object]], data: callable
):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Plaintext,  # this the the default so does not need to be specified
        style="curved",
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/plaintext/curved.txt")


def test_table_plaintext_double(
    headers: list[str], rows: list[list[object]], data: callable
):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Plaintext,  # this the the default so does not need to be specified
        style="double",
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/plaintext/double.txt")


def test_table_plaintext_simple(
    headers: list[str], rows: list[list[object]], data: callable
):
    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Plaintext,  # this the the default so does not need to be specified
        style="simple",
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/plaintext/simple.txt")


def test_table_plaintext_alignments(
    headers: list[str], rows: list[list[object]], data: callable
):
    alignments = ["left", "center", "right"]

    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Plaintext,  # this the the default so does not need to be specified
        style="simple",
        alignments=alignments,
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/plaintext/alignments.txt")


def test_table_plaintext_min_width(
    headers: list[str], rows: list[list[object]], data: callable
):
    alignments = ["left", "center", "right"]

    table = Tabulicious(
        headers=headers,
        rows=rows,
        format=Plaintext,  # this the the default so does not need to be specified
        style="simple",
        alignments=alignments,
        min_width=10,
    )

    string = table.string()

    assert isinstance(string, str)
    assert string == data("examples/plaintext/alignments-min-width-10.txt")
