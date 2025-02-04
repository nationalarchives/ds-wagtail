# This file lives here rather than in the config package, because the test runner
# does not seem able to find it there. Also the test.py setting file is being
# discovered as a test.
import django.test

from config.settings.util import strtobool


class TestStrToBool(django.test.SimpleTestCase):
    TRUTHY_VALUES = (
        "y",
        "yes",
        "t",
        "true",
        "on",
        "1",
        "Y",
        "YES",
        "T",
        "TRUE",
        "ON",
        "oN",
        "tRuE",
        "YeS",
        "Yes",
    )

    def test_truthy_values(self) -> None:
        for value in self.TRUTHY_VALUES:
            with self.subTest(value=value):
                self.assertIs(strtobool(value), True)

    FALSY_VALUES = (
        "n",
        "no",
        "f",
        "false",
        "off",
        "0",
        "N",
        "NO",
        "F",
        "FALSE",
        "OFF",
        "fALsE",
        "nO",
        "No",
        "ofF",
    )

    def test_falsy_values(self) -> None:
        for value in self.FALSY_VALUES:
            with self.subTest(value=value):
                self.assertIs(strtobool(value), False)

    INCORRECT_VALUES = (
        "",
        " ",
        "\t",
        " n",
        " no ",
        " f ",
        " false ",
        " off ",
        "random value",
    )

    def test_incorrect_values(self):
        for value in self.INCORRECT_VALUES:
            exception_message = f"invalid truth value {value!r}"
            with self.subTest(value=value, exception_message=exception_message):
                with self.assertRaises(ValueError) as cm:
                    strtobool(value)
                # We are using assertRaises instead of assertRaisesRegex
                # because we want to test values like "\t" which won't work
                # with assertRaisesRegex. Therefore we need to test the message
                # with assertEqual separately.
                self.assertEqual(str(cm.exception), exception_message)
