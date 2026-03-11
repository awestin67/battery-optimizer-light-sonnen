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

import asyncio
import logging
from datetime import timedelta

import async_timeout
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import SonnenAPI
from .const import CONF_HOST, CONF_PORT, CONF_API_TOKEN, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sonnen from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    token = entry.data[CONF_API_TOKEN]
    session = async_get_clientsession(hass)
    api = SonnenAPI(host, port, token, session)

    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            async with async_timeout.timeout(10):
                return await api.async_get_status()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sonnen_sensor",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # --- Registrera tjänster ---
    SERVICE_SCHEMA = vol.Schema({vol.Required("power"): vol.All(vol.Coerce(int), vol.Range(min=0))})

    async def handle_force_charge(call):
        """Handle the force_charge service call."""
        power = call.data.get("power", 0)
        await api.async_set_operating_mode(1)
        await asyncio.sleep(0.5)
        if await api.async_charge(power):
            await coordinator.async_request_refresh()

    async def handle_force_discharge(call):
        """Handle the force_discharge service call."""
        power = call.data.get("power", 0)
        await api.async_set_operating_mode(1)
        await asyncio.sleep(0.5)
        if await api.async_discharge(power):
            await coordinator.async_request_refresh()

    async def handle_hold(call):
        """Handle the hold service call (Manual mode, 0W)."""
        await api.async_set_operating_mode(1)
        await asyncio.sleep(0.5)
        if await api.async_charge(0):
            await coordinator.async_request_refresh()

    async def handle_auto(call):
        """Handle the auto service call (Self-consumption)."""
        if await api.async_set_operating_mode(2):
            await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "force_charge", handle_force_charge, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, "force_discharge", handle_force_discharge, schema=SERVICE_SCHEMA)
    hass.services.async_register(DOMAIN, "hold", handle_hold)
    hass.services.async_register(DOMAIN, "auto", handle_auto)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        hass.services.async_remove(DOMAIN, "force_charge")
        hass.services.async_remove(DOMAIN, "force_discharge")
        hass.services.async_remove(DOMAIN, "hold")
        hass.services.async_remove(DOMAIN, "auto")

    return unload_ok
