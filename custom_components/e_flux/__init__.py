"""The E-Flux integration."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up E-Flux from a config entry."""
    _LOGGER.debug("Setting up E-Flux integration")
    # TODO: Add code to initialize your integration here
    hass.data.setdefault(DOMAIN, {})
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading E-Flux integration")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ("sensor",))
    return unload_ok