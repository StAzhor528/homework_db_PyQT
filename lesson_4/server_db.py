from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


class ServerStorage:
    Base = declarative_base()

    def __init__(self):
        self.engine = create_engine('sqlite:///server_data_base.db3',
                                    echo=False,
                                    pool_recycle=7200)

        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)

        self.sess = Session()

    class ClientDB(Base):
        __tablename__ = 'clients'
        id = Column(Integer, primary_key=True)
        login = Column(String)
        info = Column(String)

        def __init__(self, login, info):
            self.login = login
            self.info = info

    class ClientHistoryDB(Base):
        __tablename__ = 'client_history'
        id = Column(Integer, primary_key=True)
        client = Column(ForeignKey('clients.id'))
        entry_time = Column(DateTime)
        ip_address = Column(String)

        def __init__(self, client, entry_time, ip_address):
            self.client = client
            self.entry_time = entry_time
            self.ip_address = ip_address

    class ClientContactDB(Base):
        __tablename__ = 'client_contacts'
        id = Column(Integer, primary_key=True)
        from_client = Column(ForeignKey('clients.id'))
        to_client = Column(ForeignKey('clients.id'))
        msg = Column(String)
        time = Column(DateTime)

        def __init__(self, from_client, to_client, msg, time):
            self.from_client = from_client
            self.to_client = to_client
            self.msg = msg
            self.time = time

    def user_login(self, username):
        user = self.ClientDB(username, 'bla')
        self.sess.add(user)
        self.sess.commit()

    def insert_in_contactdb(self, from_client, to_client, msg, time):
        dt = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
        from_client_id = self.sess.query(self.ClientDB).filter(self.ClientDB.login == from_client).first()
        to_client_id = self.sess.query(self.ClientDB).filter(self.ClientDB.login == to_client).first()
        contact = self.ClientContactDB(from_client_id.id, to_client_id.id, msg, dt)
        self.sess.add(contact)
        self.sess.commit()

    def del_in_contactdb(self, from_client, to_client):
        from_client_id = self.sess.query(self.ClientDB).filter(self.ClientDB.login == from_client).first()
        to_client_id = self.sess.query(self.ClientDB).filter(self.ClientDB.login == to_client).first()
        r = self.sess.query(self.ClientContactDB).filter(self.ClientContactDB.from_client == from_client_id.id,
                                                         self.ClientContactDB.to_client == to_client_id.id
                                                         ).all()

        for el in r:
            self.sess.delete(el)
        self.sess.commit()

    def get_all_users_messages(self, username):
        user = self.sess.query(self.ClientDB).filter(self.ClientDB.login == username).first()
        r = self.sess.query(self.ClientContactDB).filter(self.ClientContactDB.from_client == user.id).all()
        for el in r:
            recipient = self.sess.query(self.ClientDB).filter(self.ClientDB.id == el.to_client).first()
            print(f'Кому: {recipient.login}. Сообщение: {el.msg}. Время: {el.time}')

    def get_all_users(self):
        return self.sess.query(self.ClientDB).all()

    def get_all_messages(self):
        all_messages_list = []
        all_messages = self.sess.query(self.ClientContactDB).all()
        for message in all_messages:
            from_client = self.sess.query(self.ClientDB).filter(self.ClientDB.id == message.from_client).first()
            to_client = self.sess.query(self.ClientDB).filter(self.ClientDB.id == message.to_client).first()
            all_messages_list.append((from_client.login, to_client.login, message.msg, message.time))
        return all_messages_list



    def get_my_contacts(self, username):
        my_contacts_logins = []
        user = self.sess.query(self.ClientDB).filter(self.ClientDB.login == username).first()
        user_contacts_id = self.sess.query(self.ClientContactDB.to_client.distinct()).filter(
            self.ClientContactDB.from_client == user.id).all()
        for user_id in user_contacts_id:
            contact = self.sess.query(self.ClientDB).filter(self.ClientDB.id == user_id[0]).first()
            my_contacts_logins.append(contact.login)
        return my_contacts_logins


if __name__ == '__main__':
    s = ServerStorage()
    # s.insert_in_contactdb('test1', 'test2', 'привет', time.time())
    print(s.get_all_messeges())
