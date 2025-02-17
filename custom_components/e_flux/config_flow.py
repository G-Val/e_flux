"""Config flow for E-Flux integration."""

import logging

import voluptuous as vol
import requests  # <--- Hier is de import
import asyncio
import json

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        # OF: vol.Required("api_token"): str,
    }
)


class EFluxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for E-Flux."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                # Authenticeer met de E-Flux API
                token = await self.authenticate(
                    user_input["username"], user_input["password"]
                )
                # OF: token = await self.authenticate(user_input["api_token"])

                if token:
                    return self.async_create_entry(
                        title="E-Flux Account", data={"token": token}
                    )  # sla de token op
                else:
                    errors["base"] = "invalid_auth"  # gebruik een betere error

            except Exception as e:  # Handel exceptions af
                _LOGGER.error("Failed to authenticate with E-Flux: %s", e)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def authenticate(self, username, password):
        """Authenticate with the E-Flux API and return the token."""
        url = "https://api.e-flux.nl/1/auth/login"
        headers = {  # <--- Voeg headers dictionary toe
            "accept": "application/json",
            "content-type": "application/json",
            "origin": "https://dashboard.e-flux.io",
            "referer": "https://dashboard.e-flux.io/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36", # Basic browser user-agent
            "provider": "5e833daeadadc4003fdf7fb2", 
        }
        payload = json.dumps({"email": username, "password": password})

        try:
            response = await self.hass.async_add_executor_job(
                requests.post,  # De functie zelf (als eerste argument)
                url,           # url als positioneel argument
                data=payload,    # data/payload als positioneel argument (let op: data=...)
                headers=headers, # headers als positioneel argument (let op: headers=...)
                timeout=10      # timeout als positioneel argument (let op: timeout=...)
            )
            response.raise_for_status()
            data = response.json()
            return data["data"]["token"]
    
        except requests.exceptions.Timeout as err: # <--- Specifieke Timeout error handling
            _LOGGER.error("Timeout communicating with E-Flux API: %s", err)
            return None
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error communicating with E-Flux API: %s", err)
            return None
        except (KeyError, ValueError) as err:
            _LOGGER.error("Invalid response from E-Flux API: %s", err)
            return None