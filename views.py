from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        event_id = request.data.get('event')

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if event.available_seats <= 0:
            return Response(
                {"error": "No seats available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            registration = serializer.save()

            event.available_seats -= 1
            event.save()

            return Response(
                self.get_serializer(registration).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        registration = self.get_object()
        event = registration.event

        registration.delete()

        event.available_seats += 1
        event.save()

        return Response(status=status.HTTP_204_NO_CONTENT)