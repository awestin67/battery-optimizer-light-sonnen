# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Konfiguration för pytest."""
import os
import sys
from unittest.mock import MagicMock, AsyncMock, patch
import pytest

# Lägg till rotkatalogen i sys.path så att vi kan importera custom_components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- MOCK HOME ASSISTANT ---
# Vi måste mocka HA-moduler INNAN vi importerar komponenter
# för att slippa installera 'homeassistant' och dess tunga beroenden.

mock_hass = MagicMock()
sys.modules["homeassistant"] = mock_hass
sys.modules["homeassistant.core"] = mock_hass
sys.modules["homeassistant.config_entries"] = mock_hass
sys.modules["homeassistant.data_entry_flow"] = mock_hass
sys.modules["homeassistant.helpers"] = mock_hass
sys.modules["homeassistant.helpers.entity"] = mock_hass
sys.modules["homeassistant.helpers.update_coordinator"] = mock_hass
sys.modules["homeassistant.helpers.aiohttp_client"] = mock_hass
sys.modules["homeassistant.components"] = mock_hass
sys.modules["homeassistant.components.sensor"] = mock_hass
sys.modules["homeassistant.components.switch"] = mock_hass
sys.modules["homeassistant.const"] = mock_hass
sys.modules["homeassistant.util"] = mock_hass
sys.modules["homeassistant.exceptions"] = mock_hass

# Konfigurera nödvändiga klasser och attribut på mocken
mock_hass.config_entries = mock_hass
mock_hass.data_entry_flow = mock_hass
mock_hass.SOURCE_USER = "user"

class MockConfigFlow:
    """Mock för ConfigFlow."""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()

    def __init__(self):
        self.hass = None
    async def async_step_user(self, user_input=None):
        pass

    def async_show_form(self, *args, **kwargs):
        """Mock method for showing a form."""

    def async_create_entry(self, *args, **kwargs):
        """Mock method for creating an entry."""

    async def async_set_unique_id(self, *args, **kwargs):
        """Mock method for setting unique ID."""

    def _abort_if_unique_id_configured(self, *args, **kwargs):
        """Mock method for aborting."""
mock_hass.ConfigFlow = MockConfigFlow

class FlowResultType:
    FORM = "form"
    CREATE_ENTRY = "create_entry"
    ABORT = "abort"
mock_hass.FlowResultType = FlowResultType

class UpdateFailed(Exception):
    pass
mock_hass.UpdateFailed = UpdateFailed

class DataUpdateCoordinator:
    def __init__(self, hass, logger, name, update_method, update_interval):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_method = update_method
        self.update_interval = update_interval
        self.data = {}
        self.async_config_entry_first_refresh = AsyncMock()
        self.async_request_refresh = AsyncMock()
mock_hass.DataUpdateCoordinator = DataUpdateCoordinator

class MockEntity:
    """Basklass för att mocka HA Entity beteende."""
    _attr_name = None
    _attr_unique_id = None
    _attr_native_unit_of_measurement = None
    _attr_device_class = None
    _attr_native_value = None
    _attr_entity_category = None

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def native_unit_of_measurement(self):
        return self._attr_native_unit_of_measurement

    @property
    def device_class(self):
        return self._attr_device_class

    @property
    def native_value(self):
        return self._attr_native_value

    @property
    def entity_category(self):
        return self._attr_entity_category

class CoordinatorEntity(MockEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
    @property
    def available(self):
        return self.coordinator.last_update_success
    async def async_added_to_hass(self): pass
mock_hass.CoordinatorEntity = CoordinatorEntity

class SensorEntity(MockEntity):
    pass
mock_hass.SensorEntity = SensorEntity

class SwitchEntity:
    pass
mock_hass.SwitchEntity = SwitchEntity

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations():
    """Dummy fixture för att ersätta den från pytest-homeassistant-custom-component."""
    yield

@pytest.fixture
def hass():
    """Fixture för en mockad HA-instans."""
    hass = MagicMock()
    hass.config.components = set()
    return hass

@pytest.fixture
def mock_sonnen_client():
    """Mocka SonnenAPI klienten för att simulera batterisvar."""
    with patch(
        "custom_components.battery_optimizer_light_sonnen.api.SonnenAPI",
        autospec=True
    ) as mock_api_class:
        client = mock_api_class.return_value

        # Standard svar för status
        client.async_get_status.return_value = {
            "USOC": 85,
            "Pac_total_W": 1200,
            "Production_W": 2500,
            "Consumption_W": 1300,
            "OperatingMode": "2"
        }

        # Standard svar för att ändra läge
        client.async_set_operating_mode.return_value = True

        yield client
