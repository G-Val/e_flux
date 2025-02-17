"""Config flow for E-Flux integration."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
# importeer e-flux library (als die bestaat, anders requests gebruiken)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
        # OF: vol.Required("api_token"): str,  # Als E-Flux een API token optie heeft
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
                token = await self.authenticate(user_input["username"], user_input["password"]) # of user_input["api_token"]
                # OF: token = await self.authenticate(user_input["api_token"])

                if token:
                    return self.async_create_entry(
                        title="E-Flux Account", data={"token": token} # sla de token op
                    )
                else:
                    errors["base"] = "invalid_auth" # gebruik een betere error

            except Exception as e: # Handel exceptions af
                _LOGGER.error("Failed to authenticate with E-Flux: %s", e)
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def authenticate(self, username, password): # of (self, api_token)
        """Authenticate with the E-Flux API and return the token."""
        url = "https://api.e-flux.nl/1/auth/login"
        response = await self.hass.async_add_executor_job(
            requests.post, url, json={"email": username, "password": password}
        )

        if response.status_code == 200:
            return response.json()["data"]["token"] 
        else:
            return None

   