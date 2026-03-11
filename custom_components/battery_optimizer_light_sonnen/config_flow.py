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
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SonnenAPI
from .const import DOMAIN, CONF_HOST, CONF_PORT, DEFAULT_PORT, CONF_API_TOKEN

_LOGGER = logging.getLogger(__name__)

class SonnenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Hantera konfigurationsflödet."""

    VERSION = 1

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

    async def async_step_reconfigure(self, user_input=None):
        """Hantera omkonfigurering."""
        errors = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

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
                return self.async_update_reload_and_abort(entry, data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
            vol.Required(CONF_API_TOKEN, default=entry.data[CONF_API_TOKEN]): str,
            vol.Optional(CONF_PORT, default=entry.data.get(CONF_PORT, DEFAULT_PORT)): int,
        })

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "api_token_url": "https://community.home-assistant.io/t/sonnen-battery-and-home-assistant/16124/165"
            },
        )
