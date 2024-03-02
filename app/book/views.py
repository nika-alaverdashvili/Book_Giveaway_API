# views.py
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models import Book
from book.serializers import BookSerializer, BookDetailSerializer


class BookViewSet(viewsets.ModelViewSet):
    """View for managing book APIs."""

    queryset = Book.objects.all()
    serializer_class = BookDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve books for authenticated user."""
        return self.queryset.filter(owner=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return BookSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new book."""
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        """Handle PUT method."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Handle PATCH method."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Handle DELETE method."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
