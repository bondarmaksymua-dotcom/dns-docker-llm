Projekt: DNS + Docker + LLM

Síť

- Server IP: 192.168.100.1/24
- Klient získává IP přes DHCP
- DNS: maksym.skola.test → 192.168.100.1

Aplikace

- Aplikace běží v Docker kontejneru
- Port: 8081
- Endpointy:
  - /ping
  - /status
  - /ai

Spuštění

docker compose up -d

Test funkčnosti

ping maksym.skola.test
curl http://maksym.skola.test:8081/ping
curl http://maksym.skola.test:8081/status

Test AI

curl -X POST http://maksym.skola.test:8081/ai -H "Content-Type: application/json" -d '{"prompt":"Mám 500 Kč a koupím si věc za 320 Kč. Kolik mi zbyde?"}'

Vysvětlení

DNS přeloží doménové jméno maksym.skola.test na IP adresu serveru (192.168.100.1).
Na IP:PORT (8081) běží aplikace v Docker kontejneru.
Aplikace zpracuje požadavek a komunikuje s LLM (Ollama), který vrací odpověď.
