import unittest
from main import *

class TestMath(unittest.TestCase):

    def test_VK_POST(self):
        test_dict = {'dict': 1}
        self.assertEqual(type(VK_POST()), type(test_dict))

    def test_parser_images(self):
        YANDEX_SEARCH = 'https://yandex.ru/images/search?from=tabbar&nomisspell=1&text=%D0%BF%D1%80%D0%B0%D0%B2%D0%BE%D1%81%D0%BB%D0%B0%D0%B2%D0%BD%D1%8B%D0%B5%20%D0%BE%D1%82%D0%BA%D1%80%D1%8B%D1%82%D0%BA%D0%B8%20%D1%81%20%D0%BD%D0%B0%D0%B4%D0%BF%D0%B8%D1%81%D1%8F%D0%BC%D0%B8&source=related-0'
        self.assertTrue(parser_images(YANDEX_SEARCH))

if __name__ == "__main__":
    unittest.main()