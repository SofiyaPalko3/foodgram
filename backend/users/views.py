from api.serializers import CustomUserSerializer, FollowSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    """Вьюсет пользователей."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=['GET'], detail=False,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Список подписок."""
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data,
                                           status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST', 'DELETE'])
    def subscribe(self, request, pk=None):
        """Подписаться или отписаться"""
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if user == author:
            return Response({'errors': 'Ошибка подписки'},
                            status=status.HTTP_400_BAD_REQUEST)
        data = {
            'user': user.id,
            'author': author.id,
        }
        if request.method == 'POST':
            serializer = FollowSerializer(data=data,
                                          context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            try:
                unfollow = Follow.objects.get(user=request.user, author=author)
                unfollow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Follow.DoesNotExist:
                return Response({'errors': 'Ошибка отписки'},
                                status=status.HTTP_400_BAD_REQUEST)
