"""Unit-тесты сервера"""

import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from server import process_client_message

class TestServer(unittest.TestCase):
    msg_ok = {RESPONSE: 200}
    msg_error = {RESPONSE: 400,
                 ERROR: 'Bad Request'}

    def test_ok(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'Guest', STATUS: "Привет, я тут!"}}), self.msg_ok)

    def test_wrong_action(self):
        self.assertEqual(process_client_message(
            {ACTION: 'Error', TIME: 1, USER: {ACCOUNT_NAME: 'Guest', STATUS: "Привет, я тут!"}}), self.msg_error)

    def test_no_action(self):
        self.assertEqual(process_client_message(
            {TIME: 1, USER: {ACCOUNT_NAME: 'Guest', STATUS: "Привет, я тут!"}}), self.msg_error)

    def test_no_time_error(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest', STATUS: "Привет, я тут!"}}), self.msg_error)

    def test_wrong_account_name(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'Not guest', STATUS: "Привет, я тут!"}}), self.msg_error)

    def test_no_user(self):
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1}), self.msg_error)

if __name__ == '__main__':
    unittest.main()
