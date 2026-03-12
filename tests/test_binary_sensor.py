# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Tester för binary sensor."""
from unittest.mock import MagicMock
from custom_components.battery_optimizer_light_sonnen.binary_sensor import SonnenConnectivitySensor
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import EntityCategory

def test_connectivity_sensor_connected():
    """Testa att sensorn är PÅ när uppdatering lyckas."""
    # 1. Mocka coordinator och entry
    coordinator = MagicMock()
    coordinator.last_update_success = True

    entry = MagicMock()
    entry.entry_id = "test_entry"

    # 2. Skapa sensor
    sensor = SonnenConnectivitySensor(coordinator, entry)

    # 3. Verifiera egenskaper
    assert sensor.is_on is True
    # Tack vare uppdateringen i conftest.py jämför vi nu strängen "connectivity"
    assert sensor.device_class == BinarySensorDeviceClass.CONNECTIVITY
    assert sensor.unique_id == "test_entry_connectivity"
    assert sensor.entity_category == EntityCategory.DIAGNOSTIC

def test_connectivity_sensor_disconnected():
    """Testa att sensorn är AV när uppdatering misslyckas."""
    coordinator = MagicMock()
    # Simulera misslyckad API-kontakt
    coordinator.last_update_success = False

    entry = MagicMock()
    entry.entry_id = "test_entry"

    sensor = SonnenConnectivitySensor(coordinator, entry)

    assert sensor.is_on is False
