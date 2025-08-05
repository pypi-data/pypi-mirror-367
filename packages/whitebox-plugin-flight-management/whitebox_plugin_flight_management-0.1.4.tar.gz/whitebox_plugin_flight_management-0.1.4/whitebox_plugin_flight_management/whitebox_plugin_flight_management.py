from whitebox import Plugin
from .handlers import FlightStartHandler, FlightEndHandler


class WhiteboxPluginFlightManagement(Plugin):
    name = "Flight Management"

    provides_capabilities = [
        "flight-management",
    ]
    slot_component_map = {
        "flight-management.trigger-button": "TriggerButton",
    }
    exposed_component_map = {
        "flight-management": {
            "trigger-button": "TriggerButton",
        }
    }

    plugin_event_map = {
        "flight.start": FlightStartHandler,
        "flight.end": FlightEndHandler,
    }

    def get_plugin_classes_map(self):
        from .services import FlightService

        return {
            "flight.FlightService": FlightService,
        }


plugin_class = WhiteboxPluginFlightManagement
