# Battery Optimizer Light - Sonnen

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate and Test](https://github.com/awestin67/battery-optimizer-light-sonnen/actions/workflows/run_tests.yml/badge.svg)](https://github.com/awestin67/battery-optimizer-light-sonnen/actions/workflows/run_tests.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

En lättviktig Home Assistant-integration för att övervaka och styra **Sonnen Batterier** via API v2.
Fokus ligger på snabb uppdatering och enkel styrning av driftlägen.

## ✨ Funktioner

*   **Sensorer:**
    *   🔋 **Batterinivå (USOC)** - Visar aktuell laddningsnivå i %.
    *   ⚡ **Effekt (W)** - Nuvarande laddning (negativt) eller urladdning (positivt).
    *   ☀️ **Produktion (W)** - Solproduktion just nu.
    *   🏠 **Förbrukning (W)** - Husets totala förbrukning.
*   **Styrning:**
    *   🔘 **Driftläge (Switch)** - Växla mellan `Self Consumption` (Automatiskt läge) och `Manual Mode`.

## 📦 Installation

### Via HACS (Rekommenderas)
1.  Se till att HACS är installerat.
2.  Gå till **HACS** -> **Integrationer**.
3.  Välj menyn (tre prickar) -> **Anpassade arkiv**.
4.  Lägg till URL: `https://github.com/awestin67/battery-optimizer-light-sonnen`.
5.  Sök efter "Battery Optimizer Light Sonnen" och klicka **Ladda ner**.
6.  Starta om Home Assistant.

### Manuell installation
1.  Ladda ner mappen `battery_optimizer_light_sonnen` från detta repo.
2.  Kopiera mappen till `custom_components/` i din Home Assistant-konfiguration.
3.  Starta om Home Assistant.

## ⚙️ Konfiguration

1.  Gå till **Inställningar** -> **Enheter & Tjänster**.
2.  Klicka på **Lägg till integration**.
3.  Sök efter **Sonnen Batteri**.
4.  Ange batteriets IP-adress (standardport är `8080`).

## Krav
*   Sonnen Batteri med **API v2** aktiverat.
*   Home Assistant 2024.1 eller senare.

## 🤖 Användning med Battery Optimizer Light

Denna integration är designad för att fungera direkt med [Battery Optimizer Light](https://github.com/awestin67/battery-optimizer-light-ha) och ersätter behovet av manuella `rest_command` och `script` i din `configuration.yaml`.

Integrationen exponerar följande:
*   En switch (`switch.sonnen_manuellt_lage`) för att växla mellan auto- och manuellt läge.
*   Fyra tjänster som matchar optimerarens kommandon: `auto` (IDLE), `hold` (HOLD), `force_charge` (CHARGE) och `force_discharge` (DISCHARGE).

### Exempelautomation

Här är ett exempel på en automation som använder denna integration för att styra batteriet baserat på optimerarens beslut. Denna automation ersätter helt de gamla skripten.

```yaml
alias: 🔋 Battery Optimizer Light - Utför Beslut (Sonnen Integration)
description: Styr Sonnen-batteriet via integrationens tjänster.
trigger:
  - platform: state
    entity_id: sensor.optimizer_light_action
  - platform: time_pattern
    minutes: /5
condition:
  - condition: not
    conditions:
      - condition: state
        entity_id: sensor.optimizer_light_action
        state:
          - unknown
          - unavailable
action:
  - variables:
      current_action: "{{ states('sensor.optimizer_light_action') }}"
      target_power: "{{ (states('sensor.optimizer_light_power') | float(0) * 1000) | int }}"
  - choose:
      - conditions: "{{ current_action == 'CHARGE' }}"
        sequence:
          - service: battery_optimizer_light_sonnen.force_charge
            data:
              power: "{{ target_power }}"
      - conditions: "{{ current_action == 'DISCHARGE' }}"
        sequence:
          - service: battery_optimizer_light_sonnen.force_discharge
            data:
              power: "{{ target_power }}"
      - conditions: "{{ current_action == 'HOLD' }}"
        sequence:
          - service: battery_optimizer_light_sonnen.hold
      - conditions: "{{ current_action == 'IDLE' }}"
        sequence:
          - service: battery_optimizer_light_sonnen.auto
mode: single
```