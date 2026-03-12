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

"""Binary sensor för Sonnen Batteri."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Konfigurera binary sensors från en config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        SonnenConnectivitySensor(coordinator, entry),
    ]

    async_add_entities(entities)

class SonnenConnectivitySensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor som visar om vi har kontakt med batteriet."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        """Initiera sensorn."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_api_status"
        # Kopplar mot översättningen i sv.json under "entity" -> "binary_sensor" -> "api_status"
        self._attr_translation_key = "api_status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Battery Optimizer Light Sonnen",
            "manufacturer": "Sonnen",
        }

    @property
    def is_on(self):
        """Returnera True om coordinatorn lyckades med senaste uppdateringen."""
        return self.coordinator.last_update_success

    @property
    def available(self) -> bool:
        """Sensorn är alltid tillgänglig för att kunna rapportera 'Frånkopplad'."""
        return True
