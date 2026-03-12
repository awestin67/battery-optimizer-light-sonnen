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
        self._attr_unique_id = f"{entry.entry_id}_connectivity"
        # Kopplar mot översättningen i sv.json under "entity" -> "binary_sensor" -> "connectivity"
        self._attr_translation_key = "connectivity"

    @property
    def is_on(self):
        """Returnera True om coordinatorn lyckades med senaste uppdateringen."""
        return self.coordinator.last_update_success
