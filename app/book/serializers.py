# serializers.py

from rest_framework import serializers
from core.models import Book, Author, Genre, Condition


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model."""

    class Meta:
        model = Author
        fields = ['name']


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for the Genre model."""

    class Meta:
        model = Genre
        fields = ['name']


class ConditionSerializer(serializers.ModelSerializer):
    """Serializer for the Condition model."""

    class Meta:
        model = Condition
        fields = ['name']


class BookSerializer(serializers.ModelSerializer):
    """Serializer for the Book model."""

    author = AuthorSerializer()
    genre = GenreSerializer()
    condition = ConditionSerializer()

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'condition', 'pickup_location', 'is_available']


class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer for book detail view."""

    author = AuthorSerializer()
    genre = GenreSerializer()
    condition = ConditionSerializer()

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'condition', 'pickup_location', 'is_available']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.pickup_location = validated_data.get('pickup_location', instance.pickup_location)
        instance.is_available = validated_data.get('is_available', instance.is_available)

        # Update author
        author_data = validated_data.pop('author', None)
        if author_data:
            instance.author, _ = Author.objects.get_or_create(**author_data)

        # Update genre
        genre_data = validated_data.pop('genre', None)
        if genre_data:
            instance.genre, _ = Genre.objects.get_or_create(**genre_data)

        # Update condition
        condition_data = validated_data.pop('condition', None)
        if condition_data:
            instance.condition, _ = Condition.objects.get_or_create(**condition_data)

        instance.save()
        return instance
