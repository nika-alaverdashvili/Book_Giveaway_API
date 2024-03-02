"""
Tests for book APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Author, Genre, Condition, Book
from book.serializers import BookSerializer

BOOKS_URL = reverse('book:book-list')


def create_book(user, author, genre, condition, **params):
    """Create and return a sample book."""
    defaults = {
        'title': 'Sample book title',
        'pickup_location': 'Sample pickup location',
        'is_available': True,
    }
    defaults.update(params)

    book = Book.objects.create(owner=user, author=author, genre=genre, condition=condition, **defaults)
    return book


class PublicBookAPITests(TestCase):
    """Test unauthenticated book API access."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required for retrieving books."""
        res = self.client.get(BOOKS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookAPITests(TestCase):
    """Test authenticated book API access."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.author = Author.objects.create(name='Test Author')
        self.genre = Genre.objects.create(name='Test Genre')
        self.condition = Condition.objects.create(name='Test Condition')
        self.client.force_authenticate(self.user)

    def test_retrieve_books(self):
        """Test retrieving a list of books."""
        create_book(user=self.user, author=self.author, genre=self.genre, condition=self.condition)
        create_book(user=self.user, author=self.author, genre=self.genre, condition=self.condition)

        res = self.client.get(BOOKS_URL)

        books = Book.objects.all().order_by('-id')
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_book_list_limited_to_user(self):
        """Test that only books for the authenticated user are returned."""
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='password123',
        )
        create_book(user=other_user, author=self.author, genre=self.genre, condition=self.condition)
        create_book(user=self.user, author=self.author, genre=self.genre, condition=self.condition)

        res = self.client.get(BOOKS_URL)

        books = Book.objects.filter(owner=self.user)
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
