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


"""Switch-plattform för att styra batteriet."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    api = data["api"]

    async_add_entities([SonnenManualModeSwitch(coordinator, api)])

class SonnenManualModeSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, api):
        super().__init__(coordinator)
        self._api = api
        self._attr_name = "Sonnen Manuellt Läge"
        self._attr_unique_id = "sonnen_manual_mode"

    @property
    def is_on(self):
        # Antagande: OperatingMode "1" är manuell
        current_mode = self.coordinator.data.get("OperatingMode")
        return str(current_mode) == "1"

    async def async_turn_on(self, **kwargs):
        if await self._api.async_set_operating_mode(1):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        # Antagande: 2 är standardläge (Self-Consumption)
        if await self._api.async_set_operating_mode(2):
            await self.coordinator.async_request_refresh()
