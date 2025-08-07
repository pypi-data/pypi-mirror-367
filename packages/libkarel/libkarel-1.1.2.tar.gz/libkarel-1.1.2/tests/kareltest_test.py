#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Pruebas unitarias de libkarel."""

import unittest

from libkarel import kareltest


@unittest.skipUnless(__name__ == '__main__', 'needs to be run by itself')
class TestKareltest(kareltest.TestCase):
    """Pruebas de libkarel."""
    def test_input(self) -> None:
        """Prueba de input."""
        self.assertEqual(self.input.w, 100)
        self.assertEqual(self.input.h, 100)

    def test_output(self) -> None:
        """Prueba de output."""
        self.assertEqual(self.output.resultado, 'FIN PROGRAMA')
        self.assertEqual(self.output.error, False)

    def test_reachable_cells(self) -> None:
        """Prueba de celdas alcanzables."""
        self.assertEqual(len(self.reachableCells()), 100 * 100)

    def test_assertions(self) -> None:
        """Prueba de aseveraciones."""
        self.assertTightWorldSize()
        self.assertNoInnerWalls()


if __name__ == '__main__':
    kareltest.main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
