from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema

from .models import User, Friendship
from .serializers import UserSerializer, FriendshipSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(operation_summary="Получение списка пользователей")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_summary="Создание нового пользователя")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(operation_summary="Получение пользователя по id")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Изменение пользователя")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_summary="Частичное изменение пользователя")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_summary="Удаление пользователя")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class FriendshipCreateView(generics.CreateAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer

    @swagger_auto_schema(operation_summary="Создание запроса на дружбу")
    def post(self, request, *args, **kwargs):
        from_user_id = request.data.get('from_user')
        to_user_id = request.data.get('to_user')

        if from_user_id == to_user_id:
            return Response({'error': 'From_user_id and to_user_id are equal.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not from_user_id or not to_user_id:
            return Response({'error': 'Both from_user and to_user fields are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the friendship already exists and status of existed != rejected
        friendship_exists = Friendship.objects.filter(from_user_id=from_user_id,
                                                      to_user_id=to_user_id
                                                      ).exclude(status='rejected').exists()
        if friendship_exists:
            return Response({'error': 'Friendship already exists (accepted or pending).'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the reverse friendship exists
        reverse_friendship_exists = Friendship.objects.filter(
            from_user_id=to_user_id,
            to_user_id=from_user_id
            ).exists()
        if reverse_friendship_exists:
            # Accept the reverse friendship automatically
            reverse_friendship = Friendship.objects.get(from_user_id=to_user_id,
                                                        to_user_id=from_user_id)
            reverse_friendship.status = 'accepted'
            reverse_friendship.save()

            response_data = {}
            response_data['id'] = reverse_friendship.pk
            response_data['status'] = reverse_friendship.status
            response_data['from_user'] = reverse_friendship.from_user.pk
            response_data['to_user'] = reverse_friendship.to_user.pk
            return Response(response_data, status=status.HTTP_202_ACCEPTED)

        # Create the friendship with status 'pending'
        request.data['status'] = 'pending'
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data
        response_data['id'] = serializer.instance.pk  # Add friendship ID to the response
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class FriendshipUpdateView(generics.UpdateAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer

    @swagger_auto_schema(operation_summary="Обновление запроса по id запроса")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_summary="Частичное обновление запроса по id запроса")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class FriendshipStatusView(generics.RetrieveAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer

    @swagger_auto_schema(operation_summary="Получение статуса заявки по id заявки")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FriendshipDeleteView(generics.DestroyAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer

    @swagger_auto_schema(operation_summary="Удаление статуса заявки по id заявки")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class OutgoingFriendshipRequestsView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Friendship.objects.filter(from_user_id=user_id, status='pending')
    
    @swagger_auto_schema(operation_summary="Получение исходящих заявок в друзья")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class IncomingFriendshipRequestsView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Friendship.objects.filter(to_user_id=user_id, status='pending')
    
    @swagger_auto_schema(operation_summary="Получение входящих заявок в друзья")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AcceptedFriendshipRequestsView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Friendship.objects.filter(Q(from_user_id=user_id, status='accepted') |
                                         Q(to_user_id=user_id, status='accepted'))

    @swagger_auto_schema(operation_summary="Получение подтвержденных заявок в друзья")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FriendsListView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        friendship_ids = Friendship.objects.filter(
            Q(from_user_id=user_id, status='accepted') |
            Q(to_user_id=user_id, status='accepted')
            ).values_list('from_user_id', 'to_user_id')
        friend_ids = set()
        for from_user_id, to_user_id in friendship_ids:
            if from_user_id == user_id:
                friend_ids.add(to_user_id)
            else:
                friend_ids.add(from_user_id)
        return User.objects.filter(id__in=friend_ids)

    @swagger_auto_schema(operation_summary="Получение списка друзей")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)



class UserFriendshipStatusView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        friend_id = self.kwargs.get('friend_id')
        return Friendship.objects.filter(
            (Q(from_user_id=user_id, to_user_id=friend_id)) |
            (Q(from_user_id=friend_id, to_user_id=user_id))
        )

    @swagger_auto_schema(operation_summary="Получение статуса заявок \
                         с определенным пользователем")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class UserFriendshipUpdateView(generics.UpdateAPIView):
    serializer_class = FriendshipSerializer
    lookup_field = 'from_user_id'

    def get_queryset(self):
        user_id = self.kwargs.get('from_user_id')
        friend_id = self.kwargs.get('friend_id')
        print(user_id,friend_id)
        return Friendship.objects.filter(from_user_id=user_id,
                                         to_user_id=friend_id,
                                         status='pending')

    def perform_update(self, serializer):
        serializer.save(status=self.request.data['status'])

    @swagger_auto_schema(operation_summary="Обновление заявки с \
                         использованием id пользователя и id его друга")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление заявки с \
                         использованием id пользователя и id его друга")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

@api_view(['GET'])
def api_root(request, format=None):
    base_url = request.build_absolute_uri('/')
    return Response({
        'swagger': f'{base_url}swagger/',
        'redoc': f'{base_url}redoc/',
    })
