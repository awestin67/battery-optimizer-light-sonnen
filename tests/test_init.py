# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Tester för init."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from custom_components.battery_optimizer_light_sonnen import async_setup_auto_control, DOMAIN
from custom_components.battery_optimizer_light_sonnen.const import CONF_AUTO_CONTROL

@pytest.mark.asyncio
async def test_auto_control_setup(hass):
    """Testa att lyssnaren sätts upp korrekt."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.options = {CONF_AUTO_CONTROL: True}

    # Mocka data struktur
    api = AsyncMock()
    coordinator = MagicMock()
    hass.data = {
        DOMAIN: {
            "test_entry": {
                "api": api,
                "coordinator": coordinator,
                "auto_control_listener": None
            }
        }
    }

    # Mocka async_track_state_change_event
    with patch("custom_components.battery_optimizer_light_sonnen.async_track_state_change_event") as mock_track:
        await async_setup_auto_control(hass, entry)

        mock_track.assert_called_once()
        # Verify arguments: hass, ["sensor.optimizer_light_action"], callback
        assert mock_track.call_args[0][1] == ["sensor.optimizer_light_action"]

        # Verify listener is stored
        assert hass.data[DOMAIN]["test_entry"]["auto_control_listener"] == mock_track.return_value

@pytest.mark.asyncio
async def test_auto_control_logic(hass):
    """Testa logiken inuti lyssnaren."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.options = {CONF_AUTO_CONTROL: True}

    coordinator = MagicMock()
    # Standardvärden
    coordinator.data = {"Pac_total_W": 200, "OperatingMode": "1"}

    hass.data = {
        DOMAIN: {
            "test_entry": {
                "api": AsyncMock(),
                "coordinator": coordinator,
                "auto_control_listener": None
            }
        }
    }
    hass.services.async_call = AsyncMock()

    with patch("custom_components.battery_optimizer_light_sonnen.async_track_state_change_event") as mock_track:
        await async_setup_auto_control(hass, entry)
        # Hämta callbacken som registrerades
        callback = mock_track.call_args[0][2]

        # --- Testfall: CHARGE ---
        event = MagicMock()
        event.data = {"new_state": MagicMock(state="CHARGE")}
        hass.states.get.return_value = MagicMock(state="3.5") # 3500 W

        await callback(event)
        hass.services.async_call.assert_called_with(DOMAIN, "force_charge", {"power": 3500})

        # --- Testfall: HOLD (med filter > 100W) ---
        event.data = {"new_state": MagicMock(state="HOLD")}
        coordinator.data["Pac_total_W"] = 500 # Mer än 100W, ska trigga
        await callback(event)
        hass.services.async_call.assert_called_with(DOMAIN, "hold", {})

        # --- Testfall: HOLD (filter blockerar) ---
        hass.services.async_call.reset_mock()
        coordinator.data["Pac_total_W"] = 50 # Mindre än 100W, ska INTE trigga
        await callback(event)
        hass.services.async_call.assert_not_called()

        # --- Testfall: IDLE ---
        event.data = {"new_state": MagicMock(state="IDLE")}
        await callback(event)
        hass.services.async_call.assert_called_with(DOMAIN, "auto", {})
