# custom_components/my_integration/integration.py

import logging

from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "my_integration"

class MyIntegrationSensor(Entity):
    """Representation of a sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._state = None

    async def async_update(self):
        """Update the sensor value."""
        # Add the update code here, if any
        self._state = "Sample State"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "My Integration Sensor"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
