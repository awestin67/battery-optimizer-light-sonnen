# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Tester för sensorer."""
from unittest.mock import MagicMock
from custom_components.battery_optimizer_light_sonnen.sensor import SonnenSensor
from homeassistant.const import EntityCategory

def test_sonnen_sensor_values():
    """Testa att sensorn hämtar rätt värde från coordinatorn."""
    # 1. Skapa en mockad coordinator med data
    coordinator = MagicMock()
    coordinator.data = {
        "USOC": 85,
        "Pac_total_W": 1500,
        "OperatingMode": "2"
    }

    # 2. Skapa sensorn
    # Argument: coordinator, json_key, name, unit, device_class
    sensor = SonnenSensor(coordinator, "USOC", "Batterinivå", "%", "battery", {}, None)

    # 3. Verifiera egenskaper
    assert sensor.name == "Sonnen Batterinivå"
    assert sensor.unique_id == "sonnen_USOC"
    assert sensor.native_unit_of_measurement == "%"
    assert sensor.device_class == "battery"
    assert sensor.entity_category is None

    # 4. Verifiera värdet
    assert sensor.native_value == 85

def test_sonnen_sensor_missing_data():
    """Testa vad som händer om datat saknas."""
    coordinator = MagicMock()
    coordinator.data = {} # Tomt data

    sensor = SonnenSensor(coordinator, "USOC", "Batterinivå", "%", "battery", {}, None)

    # Borde returnera None om nyckeln saknas
    assert sensor.native_value is None

def test_diagnostic_sensor():
    """Testa att diagnostic entity sätts korrekt."""
    coordinator = MagicMock()
    coordinator.data = {"SystemStatus": "OnGrid"}

    sensor = SonnenSensor(
        coordinator, "SystemStatus", "System Status", None, None, {}, EntityCategory.DIAGNOSTIC
    )

    assert sensor.entity_category == EntityCategory.DIAGNOSTIC
    assert sensor.native_value == "OnGrid"
