from __future__ import annotations

import abc


class Format(object):
    """The Format base class provides support for creating subclasses that generate
    representations of the provided tabular data such as Plaintext, Markdown & HTML."""

    _table: Tabulicious = None

    def __init__(self, table: Tabulicious, **kwargs):
        self._table = table

    @property
    def table(self) -> Tabulicious:
        return self._table

    @abc.abstractmethod
    def string(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def print(self):
        raise NotImplementedError
