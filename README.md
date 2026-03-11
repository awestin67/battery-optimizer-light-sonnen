# Battery Optimizer Light Sonnen

<img src="https://raw.githubusercontent.com/awestin67/battery-optimizer-light-sonnen/main/custom_components/battery_optimizer_light_sonnen/logo.png" alt="Logo" width="200"/>

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate and Test](https://github.com/awestin67/battery-optimizer-light-sonnen/actions/workflows/run_tests.yml/badge.svg)](https://github.com/awestin67/battery-optimizer-light-sonnen/actions/workflows/run_tests.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

En lättviktig Home Assistant-integration för att övervaka och styra **Sonnen Batterier** via API v2.
Fokus ligger på snabb uppdatering och enkel styrning av driftlägen.

## ✨ Funktioner

*   **Sensorer:**
    *   🔋 **Batterinivå (USOC)** - Visar aktuell laddningsnivå i %.
    *   ⚡ **Effekt (W)** - Nuvarande laddning (negativt) eller urladdning (positivt).
    *   ☀️ **Solproduktion (W)** - Solproduktion just nu.
    *   🏠 **Husförbrukning (W)** - Husets totala förbrukning.
    *   📉 **Virtual Load (W)** - Beräknad nettolast (Konsumtion - Produktion).
*   **Styrning:**
    *   🔘 **Driftläge (Switch)** - Växla mellan `Self Consumption` (Automatiskt läge) och `Manual Mode`.
    *   🛠 **Tjänster** - `force_charge`, `force_discharge`, `hold` och `auto` för avancerad styrning.

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
3.  Sök efter **Battery Optimizer Light Sonnen**.
4.  Ange batteriets IP-adress (standardport är `80`).
5.  Ange din **API Token** (Auth-Token). Se denna tråd för tips om hur du hittar den.

## Krav
*   Sonnen Batteri med **API v2** aktiverat.
*   **Auth-Token** krävs för att kunna styra batteriet. Logga in på ditt batteri [http://<IP-ADRESS>/dash/login] som user och välj Software integration och därefter slå på JSON API, Read och Write. Kopiera Auth-Token.
*   Home Assistant 2024.1 eller senare.

## 🤖 Användning med Battery Optimizer Light

Denna integration är designad för att fungera direkt med [Battery Optimizer Light](https://github.com/awestin67/battery-optimizer-light-ha) och ersätter behovet av manuella `rest_command` och `script` i din `configuration.yaml`.

### Automatisk Styrning

Denna integration kan automatiskt lyssna på beslut från `Battery Optimizer Light` och styra ditt batteri, vilket eliminerar behovet av en separat automation.

1.  Gå till **Inställningar** -> **Enheter & Tjänster** och klicka på **Konfigurera** för `Battery Optimizer Light Sonnen`.
2.  Kryssa i rutan **Aktivera automatisk styrning**.

Integrationen kommer nu att lyssna på `sensor.optimizer_light_action` och agera därefter. Om du föredrar att använda egna automationer kan du lämna rutan urkryssad och använda de inbyggda tjänsterna (`force_charge`, `hold`, etc.) manuellt.

### Manuell Automation (Valfritt)

Om du **inte** aktiverar automatisk styrning, kan du använda denna automation för att koppla ihop Optimizer Light med Sonnen-integrationen:

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
      # HOLD: Skickar bara kommando om batteriet rör sig mer än 100W (Snack-filter)
      - conditions: "{{ current_action == 'HOLD' and states('sensor.sonnen_effekt_totalt') | float(0) | abs > 100 }}"
        sequence:
          - service: battery_optimizer_light_sonnen.hold
      # IDLE: Växla bara till auto om vi är i manuellt läge (switchen är på)
      - conditions: "{{ current_action == 'IDLE' and is_state('switch.sonnen_manuellt_lage', 'on') }}"
        sequence:
          - service: battery_optimizer_light_sonnen.auto
mode: single
```