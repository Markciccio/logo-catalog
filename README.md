# SOFELYWALLET Logo Catalog

Repository per il catalogo loghi remoto usato dall'app SOFELYWALLET.

## Struttura

- `catalog.json`: manifesto usato dall'app.
- `logos/`: immagini logo (`.png`, `.jpg`, `.jpeg`, `.webp`).
- `brand-map.json`: alias e nomi visualizzati per normalizzare i marchi.
- `tools/build_catalog.py`: genera automaticamente `catalog.json` dai file in `logos/`.

## Requisiti naming file

- Nome file consigliato: chiave marca in minuscolo.
- Esempio: `esselunga.png`, `carrefour.png`, `lidl.png`.

La chiave usata dall'app viene derivata dal nome file (senza estensione).

## Aggiornamento catalogo

1. Copia i nuovi loghi in `logos/`.
2. Esegui:

```bash
python tools/build_catalog.py --base-url "https://raw.githubusercontent.com/TUO-UTENTE/logo-catalog/main/logos" --brand-map "brand-map.json"
```

3. Commit e push su GitHub.

L'app scarichera' `catalog.json` e poi i loghi dal `base-url`.

## Nota marchi/copyright

- I loghi e i marchi appartengono ai rispettivi proprietari.
- Usa questo catalogo solo se hai diritto all'uso delle immagini.
- Per ridurre il rischio legale: tieni il repo privato e usa l'app in ambito personale/non commerciale.
- Se pubblichi l'app su store pubblici, valuta di rimuovere i loghi di terzi e usare solo loghi autorizzati.

## URL catalogo per l'app

Dopo aver pubblicato il repo, imposta nell'app:

`https://raw.githubusercontent.com/TUO-UTENTE/logo-catalog/main/catalog.json`
