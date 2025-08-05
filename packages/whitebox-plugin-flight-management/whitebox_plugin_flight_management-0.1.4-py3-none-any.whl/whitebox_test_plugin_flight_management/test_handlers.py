from unittest.mock import patch
from django.test import TestCase

from whitebox_plugin_flight_management.handlers import (
    FlightStartHandler,
    FlightEndHandler,
)


class TestFlightStartHandler(TestCase):
    @patch(
        "whitebox_plugin_flight_management.services.FlightService.start_flight_session"
    )
    async def test_handle(self, mock_start_flight_session):
        sentinel = object()
        mock_start_flight_session.return_value = sentinel

        handler = FlightStartHandler()
        response = await handler.handle({})

        mock_start_flight_session.assert_awaited_once()
        self.assertEqual(
            response,
            {
                "flight_session": sentinel,
            },
        )


class TestFlightEndHandler(TestCase):
    @patch(
        "whitebox_plugin_flight_management.services.FlightService.end_flight_session"
    )
    async def test_handle(self, mock_end_flight_session):
        sentinel = object()
        mock_end_flight_session.return_value = sentinel

        handler = FlightEndHandler()
        response = await handler.handle({})

        mock_end_flight_session.assert_awaited_once()
        self.assertEqual(
            response,
            {
                "flight_session": sentinel,
            },
        )
