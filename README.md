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