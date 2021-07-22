import unittest
from main import *

class TestMath(unittest.TestCase):

    def test_VK_POST(self):
        test_dict = {'dict': 1}
        self.assertEqual(type(VK_POST()), type(test_dict))


if __name__ == "__main__":
    unittest.main()
