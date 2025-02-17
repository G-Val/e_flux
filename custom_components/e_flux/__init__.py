"""The E-Flux integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import EFluxDataCoordinator  # Importeer je coordinator


_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up E-Flux from a config entry."""
    _LOGGER.debug("Setting up E-Flux integration")

    # 1. Haal de token op uit de config entry (nadat de gebruiker deze heeft ingevoerd via de config flow)
    token = entry.data["token"]

    # 2. Maak een instantie van de DataUpdateCoordinator aan
    coordinator = EFluxDataCoordinator(hass, token)

    # 3. Haal de data *eenmalig* op bij het opstarten (belangrijk!)
    await coordinator.async_config_entry_first_refresh()

    # 4. Sla de coordinator op in hass.data, zodat andere onderdelen (zoals je sensoren) erbij kunnen
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # 5. Laad de platformen (in dit geval, alleen de sensor)
    await hass.config_entries.async_forward_entry_setup(entry, Platform.SENSOR)
    # Als je meer platformen hebt (bijv. binary_sensor, switch), voeg ze dan hier toe:
    # await hass.config_entries.async_forward_entry_setup(entry, Platform.BINARY_SENSOR)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading E-Flux integration")

    # Ontlaad de platformen
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Verwijder de coordinator uit hass.data (als de integratie wordt verwijderd)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)