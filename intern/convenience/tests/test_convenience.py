import unittest

from ...convenience import parse_fquri, InvalidURIError


class TestFQURIParser(unittest.TestCase):
    """
    """

    def test_empty_string_fails(self):
        with self.assertRaises(InvalidURIError):
            parse_fquri("")

    def test_boss_uri_fails_without_protocol(self):
        with self.assertRaises(InvalidURIError):
            parse_fquri("https://api.bossdb.io/Bock/bock11/image")

    def test_boss_uri_with_token(self):
        remote, resource = parse_fquri(
            "bossdb://https://api.bossdb.io/Bock/bock11/image", token="public"
        )
        self.assertEqual(remote._token_volume, "public")
