"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Author, Genre, Condition, Book, User


class ModelTests(TestCase):
    """Test models."""
    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ('test1@EXAMPLE.com', 'test1@example.com'),
            ('Test2@Example.com', 'Test2@example.com'),
            ('TEST3@EXAMPLE.com', 'TEST3@example.com'),
            ('test4@example.COM', 'test4@example.com'),
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class BookModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test data for the Author, Genre, and Condition models
        cls.author = Author.objects.create(name='Test Author')
        cls.genre = Genre.objects.create(name='Test Genre')
        cls.condition = Condition.objects.create(name='Test Condition')

        # Create a test user
        cls.user = get_user_model().objects.create_user(email='test@example.com', password='testpassword')

    def setUp(self):
        # Create a test Book instance
        self.book = Book.objects.create(
            title='Test Book',
            author=self.author,
            genre=self.genre,
            condition=self.condition,
            owner=self.user,
            pickup_location='Test Pickup Location'
        )

    def test_book_creation(self):
        # Test if the Book instance is created successfully
        self.assertTrue(isinstance(self.book, Book))
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.author, self.author)
        self.assertEqual(self.book.genre, self.genre)
        self.assertEqual(self.book.condition, self.condition)
        self.assertEqual(self.book.owner, self.user)
        self.assertEqual(self.book.pickup_location, 'Test Pickup Location')
        self.assertTrue(self.book.is_available)

    def test_book_str_representation(self):
        # Test the __str__ method of the Book model
        expected_str = f'{self.book.title} by {self.author}'
        self.assertEqual(str(self.book), expected_str)
