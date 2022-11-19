import sqlalchemy
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker

engine = create_engine('sqlite:///server_data_base.db3',
                       echo=False,
                       pool_recycle=7200)

metadata = MetaData()

client_table = Table('clients', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('login', String),
                     Column('info', String),
                     )

client_history_table = Table('client_history', metadata,
                             Column('id', Integer, primary_key=True),
                             Column('client', ForeignKey('clients.id')),
                             Column('entry_time', DateTime),
                             Column('ip_address', String),
                             )

client_contacts = Table('client_contacts', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('from', ForeignKey('clients.id')),
                        Column('to', ForeignKey('clients.id')),
                        )
metadata.create_all(engine)


class Client:
    def __init__(self, login, info):
        self.login = login
        self.info = info

    def __repr__(self):
        return f'Client: login - {self.login}, info - {self.info}'


class ClientHistory:
    def __init__(self, client, entry_time, ip_address):
        self.client = client
        self.entry_time = entry_time
        self.ip_address = ip_address


class ClientContact:
    def __init__(self, from_client, to_client):
        self.from_client = from_client
        self.to_client = to_client


mapper(Client, client_table)
mapper(ClientHistory, client_history_table)
mapper(ClientContact, client_contacts)

Session = sessionmaker(bind=engine)

sess = Session()

