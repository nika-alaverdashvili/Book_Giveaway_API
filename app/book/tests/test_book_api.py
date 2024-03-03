from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Author, Genre, Condition, Book
from book.serializers import BookSerializer

BOOKS_URL = reverse('book:book-list')


def create_author(name='Test Author'):
    return Author.objects.create(name=name)


def create_genre(name='Test Genre'):
    return Genre.objects.create(name=name)


def create_condition(name='Test Condition'):
    return Condition.objects.create(name=name)


def create_book(user, author, genre, condition, **params):
    defaults = {
        'title': 'Sample book title',
        'pickup_location': 'Sample pickup location',
        'is_available': True,
    }
    defaults.update(params)
    return Book.objects.create(owner=user, author=author, genre=genre, condition=condition, **defaults)


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

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
        )
        cls.author = create_author()
        cls.genre = create_genre()
        cls.condition = create_condition()

    def setUp(self):
        self.client = APIClient()
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

    def test_create_book(self):
        """Test creating a new book."""
        author_data = {'name': 'strihtgng'}
        genre_data = {'name': 'string'}
        condition_data = {'name': 'string'}
        payload = {
            'title': 'strfrgijhgng',
            'author': author_data,
            'genre': genre_data,
            'condition': condition_data,
            'pickup_location': 'string',
            'is_available': True
        }

        response = self.client.post(BOOKS_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_book(self):
        """Test updating a book."""
        book = create_book(user=self.user, author=self.author, genre=self.genre, condition=self.condition)
        new_title = 'Updated Book Title'
        payload = {
            'title': new_title,
            'author': {'name': 'New Author Name'},
            'genre': {'name': 'New Genre Name'},
            'condition': {'name': 'New Condition Name'},
            'pickup_location': 'New Pickup Location',
            'is_available': False
        }

        url = reverse('book:book-detail', args=[book.id])
        response = self.client.put(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, new_title)

    def test_partial_update_book(self):
        """Test partially updating a book."""
        book = create_book(user=self.user, author=self.author, genre=self.genre, condition=self.condition)
        new_title = 'Updated Book Title'
        payload = {'title': new_title}

        url = reverse('book:book-detail', args=[book.id])
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, new_title)

    def test_delete_book(self):
        """Test deleting a book."""
        book = create_book(user=self.user, author=self.author, genre=self.genre, condition=self.condition)

        url = reverse('book:book-detail', args=[book.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())
