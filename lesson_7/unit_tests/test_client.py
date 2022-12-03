"""Unit-тесты клиента"""

import sys
import os
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence, process_response_ans


class TestClass(unittest.TestCase):

    def test_create_presence(self):
        test = create_presence()
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_create_answer_200(self):
        self.assertEqual(process_response_ans({RESPONSE: 200}), '200 : OK')

    def test_create_answer_400(self):
        self.assertEqual(process_response_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_create_answer_value_error(self):
        self.assertRaises(ValueError, process_response_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
