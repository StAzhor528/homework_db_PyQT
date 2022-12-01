"""Unit-тесты утилит"""

import sys
import os
import unittest
import json
from socket import socket, AF_INET, SOCK_STREAM

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING, MAX_PACKAGE_LENGTH, \
    DEFAULT_PORT, DEFAULT_IP_ADDRESS, MAX_CONNECTIONS
from common.utils import get_msg, send_msg


class TestClass(unittest.TestCase):
    msg_ok = {ACTION: PRESENCE,
              TIME: 1,
              USER: {
                  ACCOUNT_NAME: 'Guest'
              }
              }
    response_ok = {RESPONSE: 200}
    response_error = {RESPONSE: 400,
                      ERROR: 'Bad Request'}

    server_socket = None
    client_socket = None

    def setUp(self) -> None:
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((DEFAULT_IP_ADDRESS, DEFAULT_PORT))
        self.server_socket.listen(MAX_CONNECTIONS)

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((DEFAULT_IP_ADDRESS, DEFAULT_PORT))
        self.client, self.client_addres = self.server_socket.accept()

    def tearDown(self) -> None:
        self.client.close()
        self.client_socket.close()
        self.server_socket.close()

    def test_wrong_msg_from_client(self):
        self.assertRaises(TypeError, send_msg, self.client_socket, 'не словарь')

    def test_client_server_msg(self):
        send_msg(self.client_socket, self.msg_ok)
        response = self.client.recv(MAX_PACKAGE_LENGTH)
        response = json.loads(response.decode(ENCODING))
        self.assertEqual(self.msg_ok, response)

    def test_msg_from_server_not_dict(self):
        message = json.dumps('не словарь')
        self.client.send(message.encode(ENCODING))
        self.assertRaises(ValueError, get_msg, self.client_socket)

    def test_get_200_from_server(self):
        msg = json.dumps(self.response_ok)
        self.client.send(msg.encode(ENCODING))
        response = get_msg(self.client_socket)
        self.assertEqual(self.response_ok, response)

    def test_get_400_from_server(self):
        msg = json.dumps(self.response_error)
        self.client.send(msg.encode(ENCODING))
        response = get_msg(self.client_socket)
        self.assertEqual(self.response_error, response)


if __name__ == '__main__':
    unittest.main()
