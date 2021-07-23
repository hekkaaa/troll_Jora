import unittest
from main import *

class TestMath(unittest.TestCase):

    def test_post_vk(self):
        # Необходимо вставить значения для прохождения теста
        self.assertTrue(type(post_vk('', '', '', [''])))

    def test_parser_images(self):
        search_text = 'православные картинки с надписями'
        self.assertTrue(parse_images(search_text))

if __name__ == "__main__":
    unittest.main()