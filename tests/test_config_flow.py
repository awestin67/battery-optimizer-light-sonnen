# Battery Optimizer Light
# Copyright (C) 2026 @awestin67

"""Testar config flow."""
import pytest
from unittest.mock import patch, AsyncMock, ANY
from custom_components.battery_optimizer_light_sonnen.config_flow import SonnenConfigFlow
from custom_components.battery_optimizer_light_sonnen.const import CONF_HOST, CONF_PORT, CONF_API_TOKEN

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
