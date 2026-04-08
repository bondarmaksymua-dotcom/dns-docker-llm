Projekt: DNS + Docker + LLM

Síť

- Server IP: 192.168.100.1/24
- Klient získává IP adresu přes DHCP

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
-d '{"prompt":"Mam 500 Kc a koupim si vec za 320 Kc. Kolik mi zbyde?"}'

---

Vysvětlení

DNS přeloží doménové jméno maksym.skola.test na IP adresu serveru (192.168.100.1).
Na této IP a portu 8081 běží aplikace v Docker kontejneru.
Aplikace komunikuje s lokálním LLM (Ollama), který zpracuje dotaz a vrátí odpověď.

---

Video demo

Ukázka funkčnosti projektu (DNS, Docker, LLM):

(https://drive.google.com/file/d/1tlWjFGYoi0fWXyXMQ2dhSfpI0si2BEMA/view?usp=sharing)
