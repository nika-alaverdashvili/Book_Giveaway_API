from rest_framework import serializers
from core.models import Book, Author, Genre, Condition


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for authors."""

    class Meta:
        model = Author
        fields = ['id', 'name']
        read_only_fields = ['id']


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genres."""

    class Meta:
        model = Genre
        fields = ['id', 'name']
        read_only_fields = ['id']


class ConditionSerializer(serializers.ModelSerializer):
    """Serializer for conditions."""

    class Meta:
        model = Condition
        fields = ['id', 'name']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""

    author = AuthorSerializer()
    genre = GenreSerializer()
    condition = ConditionSerializer()
    id = serializers.IntegerField(read_only=True, source='get_next_available_id')

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'condition', 'pickup_location', 'is_available']
        read_only_fields = ['id']

    def create(self, validated_data):
        author_name = validated_data.pop('author')
        genre_name = validated_data.pop('genre')
        condition_name = validated_data.pop('condition')

        author, _ = Author.objects.get_or_create(name=author_name)
        genre, _ = Genre.objects.get_or_create(name=genre_name)
        condition, _ = Condition.objects.get_or_create(name=condition_name)

        book = Book.objects.create(
            author=author,
            genre=genre,
            condition=condition,
            **validated_data
        )

        return book


class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed book view."""

    author = AuthorSerializer()
    genre = GenreSerializer()
    condition = ConditionSerializer()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'condition', 'pickup_location', 'is_available']
        read_only_fields = ['id']

    def create(self, validated_data):
        author_data = validated_data.pop('author')
        genre_data = validated_data.pop('genre')
        condition_data = validated_data.pop('condition')

        author, _ = Author.objects.get_or_create(name=author_data['name'])
        genre, _ = Genre.objects.get_or_create(name=genre_data['name'])
        condition, _ = Condition.objects.get_or_create(name=condition_data['name'])

        book = Book.objects.create(
            author=author,
            genre=genre,
            condition=condition,
            **validated_data
        )

        return book

    def update(self, instance, validated_data):
        """Update a book instance."""
        author_data = validated_data.pop('author', None)
        genre_data = validated_data.pop('genre', None)
        condition_data = validated_data.pop('condition', None)

        if author_data:
            author, _ = Author.objects.get_or_create(name=author_data['name'])
            instance.author = author

        if genre_data:
            genre, _ = Genre.objects.get_or_create(name=genre_data['name'])
            instance.genre = genre

        if condition_data:
            condition, _ = Condition.objects.get_or_create(name=condition_data['name'])
            instance.condition = condition

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
