from django.utils import timezone

from utils.locking import aglobal_lock
from .models import FlightSession


class FlightService:
    @classmethod
    def _lock(cls):
        # Convenience method to create a lock object, as it is not reusable
        return aglobal_lock("flight_management_lock")

    @classmethod
    async def start_flight_session(cls):
        """
        Start a new flight session.

        This method initiates a flight session, triggering any registered
        callbacks or actions associated with the flight start event.

        Raises:
            ValueError: If a flight session is already in progress.

        Returns:
            FlightSession: The newly created flight session.
        """
        async with cls._lock():
            current = await FlightSession.objects.acurrent()
            if current:
                raise ValueError("A flight session is already in progress.")

            session = await FlightSession.objects.acreate()

        return session

    @classmethod
    async def end_flight_session(cls):
        """
        End the current flight session.

        This method concludes the flight session, marking it as ended and
        triggering any registered callbacks or actions associated with the
        flight end event.

        Raises:
            ValueError: If no flight session is currently in progress.

        Returns:
            FlightSession: The ended flight session.
        """
        async with cls._lock():
            current = await FlightSession.objects.acurrent()
            if not current:
                raise ValueError("No flight session is currently in progress.")

            current.ended_at = timezone.now()
            await current.asave()

        return current

    @classmethod
    async def get_current_flight_session(cls):
        """
        Retrieve the current flight session.

        Returns:
            FlightSession: The current flight session if it exists, otherwise None.
        """
        async with cls._lock():
            return await FlightSession.objects.acurrent()

    @classmethod
    async def get_flight_session_by_id(cls, session_id):
        """
        Retrieve a flight session by its ID.

        Args:
            session_id (int): The ID of the flight session to retrieve.

        Returns:
            FlightSession: The flight session with the specified ID, or None if not found.
        """
        return await FlightSession.objects.filter(id=session_id).afirst()
