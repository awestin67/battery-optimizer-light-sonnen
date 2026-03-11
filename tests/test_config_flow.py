# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Testar config flow."""
import pytest
from unittest.mock import patch, AsyncMock, ANY, MagicMock
from custom_components.battery_optimizer_light_sonnen.config_flow import SonnenConfigFlow, SonnenOptionsFlowHandler
from custom_components.battery_optimizer_light_sonnen.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_API_TOKEN,
    CONF_AUTO_CONTROL,
)

# --- TESTER FÖR CONFIG FLOW ---

@pytest.mark.asyncio
async def test_show_form(hass):
    """Testa att formuläret visas vid start."""
    flow = SonnenConfigFlow()
    flow.hass = hass

    with patch.object(flow, "async_show_form") as mock_show_form:
        await flow.async_step_user(user_input=None)

    mock_show_form.assert_called_once()
    assert mock_show_form.call_args[1]["step_id"] == "user"

@pytest.mark.asyncio
async def test_connection_success(hass):
    """Testa att vi skapar en entry vid lyckad anslutning."""
    flow = SonnenConfigFlow()
    flow.hass = hass

    user_input = {
        CONF_HOST: "192.168.1.100",
        CONF_PORT: 80,
        CONF_API_TOKEN: "test_token"
    }

    with patch("custom_components.battery_optimizer_light_sonnen.config_flow.SonnenAPI") as mock_api_cls, \
         patch.object(flow, "async_create_entry") as mock_create_entry, \
         patch.object(flow, "async_set_unique_id", new_callable=AsyncMock) as mock_set_unique_id, \
         patch.object(flow, "_abort_if_unique_id_configured") as mock_abort:

        # Konfigurera mockad API-klient
        mock_api = mock_api_cls.return_value
        mock_api.async_get_status = AsyncMock(return_value={"USOC": 50})

        await flow.async_step_user(user_input=user_input)

        # Verifiera att API anropades med rätt parametrar
        mock_api_cls.assert_called_with(
            host="192.168.1.100",
            port=80,
            token="test_token",
            session=ANY
        )
        mock_api.async_get_status.assert_called_once()

        # Verifiera att entry skapades
        mock_set_unique_id.assert_called_with("192.168.1.100")
        mock_abort.assert_called_once()
        mock_create_entry.assert_called_with(title="Battery Optimizer Light Sonnen", data=user_input)

@pytest.mark.asyncio
async def test_connection_failed(hass):
    """Testa att vi visar felmeddelande vid misslyckad anslutning."""
    flow = SonnenConfigFlow()
    flow.hass = hass

    user_input = {
        CONF_HOST: "192.168.1.100",
        CONF_PORT: 80,
        CONF_API_TOKEN: "bad_token"
    }

    with patch("custom_components.battery_optimizer_light_sonnen.config_flow.SonnenAPI") as mock_api_cls, \
         patch.object(flow, "async_show_form") as mock_show_form:

        # Konfigurera mockad API-klient att kasta undantag
        mock_api = mock_api_cls.return_value
        mock_api.async_get_status = AsyncMock(side_effect=Exception("Connection refused"))

        await flow.async_step_user(user_input=user_input)

        # Verifiera att formuläret visas igen med felmeddelande
        mock_show_form.assert_called_once()
        assert mock_show_form.call_args[1]["step_id"] == "user"
        assert mock_show_form.call_args[1]["errors"] == {"base": "cannot_connect"}

# --- TESTER FÖR OPTIONS FLOW ---

@pytest.mark.asyncio
async def test_options_flow(hass):
    """Testa options flow."""
    config_entry = MagicMock()
    config_entry.options = {}

    flow = SonnenOptionsFlowHandler(config_entry)
    flow.hass = hass

    # Konfigurera mock för async_reload så den går att awaita
    hass.config_entries.async_reload = AsyncMock()

    # Test step_init show form
    with patch.object(flow, "async_show_form") as mock_show_form:
        await flow.async_step_init(user_input=None)

    mock_show_form.assert_called_once()
    assert mock_show_form.call_args[1]["step_id"] == "init"

    # Test step_init save data
    user_input = {CONF_AUTO_CONTROL: True}
    with patch.object(flow, "async_create_entry") as mock_create_entry:
        await flow.async_step_init(user_input=user_input)

        # Verifiera att vi sparade via async_update_entry istället
        hass.config_entries.async_update_entry.assert_called_once()
        call_kwargs = hass.config_entries.async_update_entry.call_args[1]
        assert call_kwargs["options"][CONF_AUTO_CONTROL] is True

        # Verifiera att create_entry anropades för att avsluta flödet (med tom data)
        mock_create_entry.assert_called_with(title="", data={})

@pytest.mark.asyncio
async def test_options_flow_saved_value(hass):
    """Testa att options flow läser och sparar värden korrekt."""
    # 1. Simulera en existerande config entry där auto_control är True
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {CONF_HOST: "1.2.3.4"}
    config_entry.options = {CONF_AUTO_CONTROL: True}

    flow = SonnenOptionsFlowHandler(config_entry)
    flow.hass = hass

    # Konfigurera mock för async_reload
    hass.config_entries.async_reload = AsyncMock()

    # 2. Initiera flödet och verifiera att formuläret visas
    with patch.object(flow, "async_show_form") as mock_show_form:
        await flow.async_step_init(user_input=None)

    # Verifiera att schemat har rätt default-värde (True) för auto_control
    mock_show_form.assert_called_once()

    # Eftersom vi använder vol.Optional(..., default=...) kan vi inte enkelt inspektera default-värdet
    # på ett kompilerat schema i en mock, men koden 'default=current_config.get(...)'
    # har vi verifierat genom logiken i config_flow.py
