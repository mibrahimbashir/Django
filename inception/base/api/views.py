from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import RoomSerializer

from base.models import Room

@api_view(['GET'])
def routes(request):
	routes = [
		'GET /api',
		'GET /api/rooms',
		'GET /api/room/:id'
	]

	return Response(routes)

@api_view(['GET'])
def get_rooms(request):
	rooms = Room.objects.all()
	serializer = RoomSerializer(rooms, many=True)
	return Response(serializer.data)

@api_view(['GET'])
def get_room(request, pk):
	room = Room.objects.get(id=pk)
	serializer = RoomSerializer(room, many=False)
	return Response(serializer.data)