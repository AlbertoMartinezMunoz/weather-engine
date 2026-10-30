import unittest

from package.package_class import Class


class TestClassUnittest(unittest.TestCase):
    def setUp(self) -> None:
        self.c = Class()
        super().setUp()

    def test_given_class_when_method_expected_str_then_return_expected_str(self):
        expected_str = "expected string"
        self.assertEqual(expected_str, self.c.method(expected_str))


if __name__ == "__main__":
    unittest.main()
