from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q

from .models import User, Friendship
from .serializers import UserSerializer, FriendshipSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FriendshipCreateView(generics.CreateAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer

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


class FriendshipStatusView(generics.RetrieveAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer


class FriendshipDeleteView(generics.DestroyAPIView):
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer


class OutgoingFriendshipRequestsView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Friendship.objects.filter(from_user_id=user_id, status='pending')


class IncomingFriendshipRequestsView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Friendship.objects.filter(to_user_id=user_id, status='pending')


class AcceptedFriendshipRequestsView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Friendship.objects.filter(Q(from_user_id=user_id, status='accepted') |
                                         Q(to_user_id=user_id, status='accepted'))


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


class UserFriendshipStatusView(generics.ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        friend_id = self.kwargs.get('friend_id')
        return Friendship.objects.filter(
            (Q(from_user_id=user_id, to_user_id=friend_id)) |
            (Q(from_user_id=friend_id, to_user_id=user_id))
        )


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


@api_view(['GET'])
def api_root(request, format=None):
    base_url = request.build_absolute_uri('/')
    return Response({
        'swagger': f'{base_url}swagger/',
        'redoc': f'{base_url}redoc/',
    })
