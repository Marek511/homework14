import unittest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, Contact, User


class TestModels(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()

    def test_contact_model(self):
        contact = Contact(
            first_name='Steve',
            last_name='Jobs',
            email='steve.jobs@example.com',
            phone_number='777888999',
            birth_date= date(2000, 11, 11),
            additional_data='Some additional data'
        )

        self.session.add(contact)
        self.session.commit()

        retrieved_contact = self.session.query(Contact).filter_by(email='steve.jobs@example.com').first()
        self.assertIsNotNone(retrieved_contact)
        self.assertEqual(retrieved_contact.first_name, 'Steve')
        self.assertEqual(retrieved_contact.last_name, 'Jobs')
        self.assertEqual(retrieved_contact.phone_number, '777888999')

    def test_user_model(self):
        user = User(
            email='user@example.com',
            password='password123',
            refresh_token='refresh_token_value',
            is_verified=True,
            avatar='avatar_url'
        )

        self.session.add(user)
        self.session.commit()

        retrieved_user = self.session.query(User).filter_by(email='user@example.com').first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.password, 'password123')
        self.assertTrue(retrieved_user.is_verified)
        self.assertEqual(retrieved_user.avatar, 'avatar_url')


if __name__ == '__main__':
    unittest.main()
