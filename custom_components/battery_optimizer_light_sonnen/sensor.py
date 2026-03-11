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


"""Sensor-plattform för Sonnen."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    device_info = {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": "Optimizer Light Sonnen",
        "manufacturer": "Sonnen",
    }

    sensors_to_add = [
        SonnenSensor(coordinator, "USOC", "Batterinivå", "%", "battery", device_info, None),
        SonnenSensor(coordinator, "Pac_total_W", "Effekt Totalt", "W", "power", device_info, None),
        SonnenSensor(coordinator, "Production_W", "Produktion", "W", "power", device_info, None),
        SonnenSensor(coordinator, "Consumption_W", "Förbrukning", "W", "power", device_info, None),
        SonnenSensor(coordinator, "SystemStatus", "System Status", None, None, device_info, EntityCategory.DIAGNOSTIC),
    ]

    async_add_entities(sensors_to_add)

class SonnenSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, json_key, name, unit, device_class, device_info, entity_category):
        super().__init__(coordinator)
        self._json_key = json_key
        self._attr_name = f"Sonnen {name}"
        self._attr_unique_id = f"sonnen_{json_key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_device_info = device_info
        self._attr_entity_category = entity_category

    @property
    def native_value(self):
        return self.coordinator.data.get(self._json_key)
