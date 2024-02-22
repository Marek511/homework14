import unittest
from datetime import date
from pydantic import ValidationError
from src.schemas import ContactModel


class TestContactModel(unittest.TestCase):
    def test_valid_contact_model(self):
        data = {
            "name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_no": "123456789",
            "date_of_birth": "1990-01-01",
            "description": "Some description"
        }

        try:
            contact = ContactModel(**data)
        except ValidationError as e:
            self.fail(f"Validation failed: {e}")

        self.assertEqual(contact.name, "John")
        self.assertEqual(contact.last_name, "Doe")
        self.assertEqual(contact.email, "john.doe@example.com")
        self.assertEqual(contact.phone_no, "123456789")
        self.assertEqual(contact.date_of_birth, date(1990, 1, 1))
        self.assertEqual(contact.description, "Some description")

    def test_invalid_contact_model(self):
        invalid_data = {
            "name": "John",
            "last_name": "Doe",
            "email": "invalid_email",
            "phone_no": "123456789",
            "date_of_birth": "1990-01-01",
            "description": "Some description"
        }

        with self.assertRaises(ValidationError):
            _ = ContactModel(**invalid_data)


if __name__ == "__main__":
    unittest.main()
