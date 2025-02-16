"""Config flow for E-Flux integration."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import callback
from homeassistant.config_entries import SOURCE_REAUTH

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EFluxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for E-Flux."""

    VERSION = 1

    # Placeholder, wordt gevuld door async_step_oauth2
    oauth_session = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return EFluxOptionsFlowHandler(config_entry)
    
    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        # Controleren of de integratie al geconfigureerd is
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")
        
        # OAuth stap beginnen
        return await self.async_step_oauth2(None)


    async def async_step_oauth2(self, user_input=None) -> FlowResult:
        """Handle the OAuth2 flow."""

        # De OAuth implementatie ophalen (de ID van je OAuth2 applicatie in Home Assistant)
        try:
            implementation = await config_entry_oauth2_flow.async_get_config_entry_implementation(
                self.hass, "e_flux_oauth_app"  # <--- VERVANG DIT met de ID van je OAuth2 applicatie
            )
        except Exception as e:
             _LOGGER.error("Failed to get oauth implementation: %s", e)
             return self.async_abort(reason="oauth_error")

        # Maak een OAuth2 sessie aan
        self.oauth_session = config_entry_oauth2_flow.OAuth2Session(self.hass, implementation, self.flow_id)

        if user_input is None:
            # Genereer de authorisatie URL en stuur de gebruiker door
            try:
                authorization_url = await self.oauth_session.async_generate_authorize_url()
            except Exception as e:
                _LOGGER.error("Failed to generate authorization URL: %s", e)
                return self.async_abort(reason="oauth_error")

            # Stap om naar externe website te gaan (de authorisatie URL)
            return self.async_external_step(
                step_id="oauth2", url=authorization_url
            )


        # Verwerk de callback van E-Flux (met de authorizatie code)
        try:
            token = await self.oauth_session.async_fetch_token(user_input["code"])
        except Exception as err:
            _LOGGER.error("Failed to fetch token: %s", err)
            return self.async_abort(reason="oauth_error")

        # Maak de config entry aan en sla de tokens op.  Geef een titel en data mee.
        return self.async_create_entry(
            title="E-Flux Account",
            data={
                "auth_implementation": "e_flux_oauth_app",  # <--- VERVANG DIT met de ID van je OAuth2 applicatie
                "token": token,
            },
        )
    
    async def async_step_reauth(self, user_input=None) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        _LOGGER.debug("Reauthenticating")
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=vol.Schema({}),
                description_placeholders={"account": "E-Flux Account"},
            )
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_oauth2()

    async def async_on_close(self) -> None:
        """Clean up resources when the flow is closed."""
        _LOGGER.debug("Config flow closing, cleaning up.")
        if self.oauth_session:
            await self.oauth_session.async_close()

class EFluxOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for E-Flux."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "example_option",
                        default=self.options.get("example_option", True),
                    ): bool,
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title="E-Flux Options", data=self.options
        )