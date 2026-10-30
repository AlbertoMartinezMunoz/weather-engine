import pytest

from package.package_class import Class


class TestClassPytest:
    @pytest.fixture
    def set_up(self):
        c = Class()
        yield c

    def test_given_class_when_method_expected_str_then_return_expected_str(self, set_up):
        c = set_up
        expected_str = "expected string"
        assert expected_str == c.method(expected_str)
