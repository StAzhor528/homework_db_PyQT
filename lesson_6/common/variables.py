DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'
DEFAULT_CLIENT_MODE = 'listen'
CLIENTS_LISTEN_NUM = 2
CLIENTS_SEND_NUM = 2

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
FROM = 'from'
TO = 'to'
CONTACT_NAME = 'contact_name'
PUBLIC_KEY = 'public_key'
PASSWORD_HASH = 'password_hash'

STATE = 'state'
AUTH = 'auth'
REG = 'reg'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
DATA = 'data'
ALERT = 'alert'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
GET_ALL_CLIENTS = 'get_all_contacts'
GET_MY_CONTACTS = 'get_my_contacts'
ADD_CONTACT = 'add_contact'
EXIT = 'exit'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {
    RESPONSE: 202,
    ALERT: []
}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}