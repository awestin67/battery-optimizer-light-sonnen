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
from homeassistant.core import HomeAssistant, Event
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.event import async_track_state_change_event

from .api import SonnenAPI
from .const import CONF_HOST, CONF_PORT, CONF_API_TOKEN, DOMAIN, CONF_AUTO_CONTROL

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
        "auto_control_listener": None,  # Placeholder for the listener
    }

    # This will call async_setup_auto_control when options change
    entry.add_update_listener(async_update_options)

    # Initial setup of auto control
    await async_setup_auto_control(hass, entry)

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

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await async_setup_auto_control(hass, entry)

async def async_setup_auto_control(hass: HomeAssistant, entry: ConfigEntry):
    """Set up or tear down the automatic control listener."""
    domain_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = domain_data["coordinator"]

    # Cancel any existing listener
    if domain_data["auto_control_listener"]:
        _LOGGER.debug("Cancelling existing auto control listener.")
        domain_data["auto_control_listener"]()
        domain_data["auto_control_listener"] = None

    # If auto control is enabled, set up a new listener
    if entry.options.get(CONF_AUTO_CONTROL, False):
        _LOGGER.info("Automatic control from sensor.optimizer_light_action is enabled.")

        async def handle_optimizer_action_change(event: Event):
            """Handle state changes for sensor.optimizer_light_action."""
            new_state = event.data.get("new_state")
            if new_state is None or new_state.state in ("unknown", "unavailable"):
                return

            current_action = new_state.state
            _LOGGER.debug(f"Optimizer action changed to: {current_action}")

            # Get power from the other sensor
            power_state = hass.states.get("sensor.optimizer_light_power")
            if power_state is None:
                _LOGGER.warning("Could not find sensor.optimizer_light_power")
                return

            try:
                target_power = int(float(power_state.state) * 1000)
            except (ValueError, TypeError):
                _LOGGER.warning(f"Invalid power value from sensor.optimizer_light_power: {power_state.state}")
                return

            if current_action == "CHARGE":
                await hass.services.async_call(DOMAIN, "force_charge", {"power": target_power})
            elif current_action == "DISCHARGE":
                await hass.services.async_call(DOMAIN, "force_discharge", {"power": target_power})
            elif current_action == "HOLD":
                # Apply snack filter
                if abs(coordinator.data.get("Pac_total_W", 0)) > 100:
                    await hass.services.async_call(DOMAIN, "hold", {})
            elif current_action == "IDLE":
                # Apply snack filter
                if str(coordinator.data.get("OperatingMode")) == "1": # If in manual mode
                    await hass.services.async_call(DOMAIN, "auto", {})

        # Set up the listener
        domain_data["auto_control_listener"] = async_track_state_change_event(
            hass, ["sensor.optimizer_light_action"], handle_optimizer_action_change
        )


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    domain_data = hass.data[DOMAIN].get(entry.entry_id)
    if domain_data and domain_data.get("auto_control_listener"):
        domain_data["auto_control_listener"]()

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        hass.services.async_remove(DOMAIN, "force_charge")
        hass.services.async_remove(DOMAIN, "force_discharge")
        hass.services.async_remove(DOMAIN, "hold")
        hass.services.async_remove(DOMAIN, "auto")

    return unload_ok
