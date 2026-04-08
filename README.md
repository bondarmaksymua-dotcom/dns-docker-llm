Projekt: DNS + Docker + LLM

Síť

- Server IP: 192.168.100.1/24
- Klient získává IP přes DHCP

DHCP

- Scope: 192.168.100.100–192.168.100.200/24
- Option 006 (DNS): 192.168.100.1

DNS

- Zóna: skola.test
- A záznam: maksym.skola.test → 192.168.100.1

---

Aplikace

- Aplikace běží v Docker kontejneru
- Port: 8081

Endpointy

- "/ping" – test dostupnosti
- "/status" – informace o aplikaci
- "/ai" – komunikace s LLM

---

Firewall

- Povolen port 8081/tcp

---

Spuštění

docker compose up -d --build

---

Test funkčnosti

ping maksym.skola.test
curl http://maksym.skola.test:8081/ping
curl http://maksym.skola.test:8081/status

---

Test AI

curl -X POST http://maksym.skola.test:8081/ai \
-H "Content-Type: application/json" \
-d '{"prompt":"Mám 500 Kč a koupím si věc za 320 Kč. Kolik mi zbyde?"}'

---

Vysvětlení

DNS přeloží doménové jméno maksym.skola.test na IP adresu serveru (192.168.100.1).
Na této IP a portu 8081 běží aplikace v Docker kontejneru.
Aplikace přijímá požadavky, zpracuje je a komunikuje s LLM (Ollama), který vrací odpověď.
