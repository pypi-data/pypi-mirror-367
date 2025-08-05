from channels.layers import get_channel_layer

from whitebox import WebsocketEventHandler
from .services import FlightService


channel_layer = get_channel_layer()


def serialize_flight_session(session):
    """
    Serialize the flight session for sending over WebSocket.
    """
    return {
        "id": session.id,
        "started_at": session.started_at.isoformat(),
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
    }


class FlightStartHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.start` event.
    """

    default_callbacks = [
        lambda data, ctx: channel_layer.group_send(
            "flight",
            {
                "type": "flight.start",
                "flight_session": serialize_flight_session(ctx["flight_session"]),
            },
        )
    ]

    async def handle(self, data):
        session = await FlightService.start_flight_session()
        return {
            "flight_session": session,
        }

    async def return_message(self):
        """
        Return a message to be sent over the WebSocket.
        This method should be implemented by subclasses.
        """
        return {
            "type": "message",
            "message": "Flight started, enjoy your flight!",
        }


class FlightEndHandler(WebsocketEventHandler):
    """
    Handler for handling the `flight.end` event.
    """

    default_callbacks = [
        lambda data, ctx: channel_layer.group_send(
            "flight",
            {
                "type": "flight.end",
                "flight_session": serialize_flight_session(ctx["flight_session"]),
            },
        )
    ]

    async def handle(self, data):
        session = await FlightService.end_flight_session()
        return {
            "flight_session": session,
        }

    async def return_message(self):
        """
        Return a message to be sent over the WebSocket.
        This method should be implemented by subclasses.
        """
        return {
            "type": "message",
            "message": "Flight ended.",
        }
