"""Data coordinator for the E-Flux integration."""

import asyncio
import logging
from datetime import timedelta

import requests

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EFluxDataCoordinator(DataUpdateCoordinator):
    """Data coordinator for the E-Flux integration."""

    def __init__(self, hass: HomeAssistant, token: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),  # Update elke 5 minuten
        )
        self.token = token

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            data = await self.fetch_data()
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


    async def fetch_data(self):
        """Fetch data from the E-Flux API."""
        # Implementeer hier de API calls naar E-Flux
        # Gebruik self.token om te authenticeren
        # Voorbeeld:
        url = "https://api.e-flux.nl/1/sessions/mine"  # Voorbeeld URL
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = await self.hass.async_add_executor_job(
                requests.get, url, headers=headers
            )
            response.raise_for_status()
            return response.json()  # Parse the JSON response

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error communicating with E-Flux API: %s", err)
            raise UpdateFailed(f"Error communicating with E-Flux API: {err}") from err
        except (KeyError, ValueError) as err:
            _LOGGER.error("Invalid response from E-Flux API: %s", err)
            raise UpdateFailed(f"Invalid response from E-Flux API: {err}") from err