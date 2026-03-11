# Battery Optimizer Light
# Copyright (C) 2026 @awestin67
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Config flow för Sonnen Batteri."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, BooleanSelector

from .api import SonnenAPI
from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_PORT, CONF_API_TOKEN, CONF_AUTO_CONTROL

_LOGGER = logging.getLogger(__name__)

class SonnenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hantera konfigurationsflödet."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SonnenOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Hantera ett flödessteg initierat av användaren."""
        errors = {}

        if user_input is not None:
            session = async_get_clientsession(self.hass)
            api = SonnenAPI(
                host=user_input[CONF_HOST],
                port=user_input[CONF_PORT],
                token=user_input[CONF_API_TOKEN],
                session=session,
            )

            try:
                await api.async_get_status()
            except Exception:
                _LOGGER.warning("Kunde inte ansluta till Sonnen-batteriet vid %s", user_input[CONF_HOST])
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title="Battery Optimizer Light Sonnen", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_API_TOKEN): str,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "api_token_url": "https://community.home-assistant.io/t/sonnen-battery-and-home-assistant/16124/165"
            },
        )

class SonnenOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Sonnen."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Separera options (auto_control) från data (host, token, port)
            options_data = {
                CONF_AUTO_CONTROL: user_input.get(CONF_AUTO_CONTROL, False)
            }

            config_data = {
                CONF_HOST: user_input.get(CONF_HOST),
                CONF_PORT: user_input.get(CONF_PORT),
                CONF_API_TOKEN: user_input.get(CONF_API_TOKEN),
            }

            # Uppdatera huvudkonfigurationen
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                data=config_data,
                options=options_data # Spara auto_control i options
            )

            # Ladda om integrationen för att de nya inställningarna ska gälla direkt
            await self.hass.config_entries.async_reload(self._config_entry.entry_id)

            return self.async_create_entry(title="", data={})

        # Hämta nuvarande värden (data + options)
        current_config = {**self._config_entry.data, **self._config_entry.options}

        schema = vol.Schema({
            vol.Required(
                CONF_HOST, default=current_config.get(CONF_HOST)
            ): TextSelector(),
            vol.Required(
                CONF_API_TOKEN, default=current_config.get(CONF_API_TOKEN)
            ): TextSelector(),
            vol.Optional(
                CONF_PORT, default=current_config.get(CONF_PORT, DEFAULT_PORT)
            ): int,
            vol.Optional(
                CONF_AUTO_CONTROL, default=current_config.get(CONF_AUTO_CONTROL, False)
            ): BooleanSelector(),
        })

        return self.async_show_form(step_id="init", data_schema=schema)
