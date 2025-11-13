# posts/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.get_queryset()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'],)
    def my_posts(self, request):
        posts = Post.objects.get_queryset()

        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

