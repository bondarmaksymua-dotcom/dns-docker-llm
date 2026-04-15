# Finanční AI asistent

Tento projekt je webová aplikace, která využívá AI model pro odpovědi na finanční dotazy uživatele.

## Funkce aplikace

- zadání finančního dotazu přes webové rozhraní  
- odeslání dotazu na AI model  
- zobrazení odpovědi  
- ukládání historie dotazů  
- počítání celkového počtu dotazů  

## Použité technologie

- Python (Flask) – webová aplikace  
- Docker – kontejnerizace  
- Docker Compose – více služeb  
- Redis – ukládání dat  
- AI API (kurim.ithope.eu) – generování odpovědí  

## Architektura

Aplikace běží ve dvou kontejnerech:

1. app – hlavní aplikace (Flask)  
2. cache – Redis databáze  

Komunikace:
- aplikace ↔ Redis (ukládání a čtení dat)  
- aplikace ↔ AI API (HTTP request)  

## Spuštění projektu

`bash
docker compose up --build
