# Wijzigingen verkoopkansen Dynamics

Interactieve pagina voor accountmanagers die per scherm laat zien wat er in Dynamics 365 Sales
(Verkoopkansen) is veranderd: een schuifbalk tussen oud en nieuw, oranje nummers per wijziging en
uitleg over wat, waarom en wat het voor jou betekent. Er zijn twee reeksen: Nieuwe klant en Verlenging.

## Mappen

| Map | Inhoud |
| --- | --- |
| `oud/` | Originele screenshots van de oude situatie |
| `nieuw/` | Originele screenshots van de nieuwe situatie |
| `site/index.html` | De pagina, inclusief alle teksten en de posities van de nummers |
| `site/img/` | Bijgesneden en bewerkte screenshots die de pagina gebruikt |
| `tools/prepare_images.py` | Script dat `site/img/` maakt uit `oud/` en `nieuw/` |
| `tools/build_pages.py` | Script dat de pagina voor GitHub Pages klaarmaakt in `_site/` |

## Een screenshot vervangen

1. Maak een venster-screenshot (browser gemaximaliseerd, zoom 100%) en vervang het bestand in `nieuw/`
   met dezelfde naam.
2. Draai `python3 tools/prepare_images.py`. Het script snijdt de screenshot bij, hernoemt de tab
   "Tabblad" naar "Bestanden" en haalt "Prognosecategorie" weg uit Algemene informatie.
3. Verschuift er iets op het scherm, controleer dan de posities van de nummers (`box`) in
   `site/index.html`.

De teksten zelf staan in het document *Teksten Verkoopkansen vernieuwd*.

## Publiceren via GitHub Pages

Bij elke wijziging in `site/` op `main` publiceert de workflow *Publiceer pagina*
(`.github/workflows/pages.yml`) de pagina op https://bobskillstown.github.io/Dynamics-verkoopkansen/.
De workflow draait `tools/build_pages.py`, dat van `site/index.html` een volledige webpagina maakt.

Let op: de Pages-site is openbaar voor iedereen met de link, ook al is de repository privé.
