# custom_components/my_integration/__init__.py

"""The My Integration component."""

DOMAIN = "my_integration"

async def async_setup(hass, config):
    """Set up the My Integration component."""
    # Add your setup code here, if any
    _LOGGER.info("Setting up My Integration")

    # Example: Set up a sensor entity
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(config.entry_id, "sensor"))

    return True

async def async_setup_entry(hass, entry):
    """Set up the component from a config entry."""
    # Add your setup code here, if any
    _LOGGER.info("Setting up My Integration from config entry")

    return True
