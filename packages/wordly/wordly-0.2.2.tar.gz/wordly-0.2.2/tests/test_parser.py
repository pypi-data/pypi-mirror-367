"""Test DICT parser."""

from __future__ import annotations

import unittest

from tests.constants import HELP_OUTPUT, PROGRAMMING_DEFINITION
from wordly.parser import DictParser
from wordly.status_codes import Status


class TestParser(unittest.TestCase):
    """Parser tests."""

    def setUp(self) -> None:
        """Set up fixtures for each test."""
        self.line_reader = DictParser()

    def test_help(self):
        """Should parse help byte stream."""
        self.line_reader.feed(HELP_OUTPUT)

        self.assertEqual(
            self.line_reader.mapping[Status.INITIAL_CONNECTION.name],
            bytearray(b"banner info from example.org\n"),
        )
        self.assertEqual(
            self.line_reader.mapping[Status.COMMAND_COMPLETE.name], bytearray(b"ok\n")
        )
        self.assertEqual(
            self.line_reader.mapping[Status.CLOSING_CONNECTION.name],
            bytearray(b"bye [d/m/c = 0/0/0; 0.000r 0.000u 0.000s]"),
        )

    def test_define(self):
        """Should parse define byte stream."""
        self.line_reader.feed(PROGRAMMING_DEFINITION)

        self.assertEqual(
            self.line_reader.mapping[Status.INITIAL_CONNECTION.name],
            bytearray(b"banner information contained here\n"),
        )
        self.assertEqual(
            self.line_reader.mapping[Status.CLOSING_CONNECTION.name],
            bytearray(b"bye [d/m/c = 0/0/0; 0.000r 0.000u 0.000s]"),
        )
