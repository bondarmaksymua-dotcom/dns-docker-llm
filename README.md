Projekt: Finanční AI asistent (DNS + Docker + LLM)

Popis projektu

Tento projekt implementuje síťovou aplikaci, která umožňuje uživatelům zadávat jednoduché finanční dotazy a získat odpověď pomocí AI modelu.

Aplikace běží v Docker kontejneru a je dostupná přes vlastní doménu v lokální síti pomocí DNS.

---

Funkcionalita

- zpracování finančních dotazů pomocí AI
- dostupnost služby přes vlastní doménu
- běh aplikace v Docker kontejneru
- využití cache (Redis)
- integrace DNS a DHCP v síti

---

Určení projektu

Projekt slouží jako demonstrace propojení těchto technologií:

- DNS (překlad domény)
- DHCP (automatické přidělení IP adresy)
- Docker (kontejnerizace aplikace)
- AI model (Ollama)

Aplikace je určena pro uživatele v lokální síti (např. studenti), kteří mohou zadávat jednoduché finanční dotazy.

---

Síťová konfigurace

- Server IP: "192.168.100.1/24"
- Klient získává IP adresu přes DHCP
- DNS záznam:
  - "maksym.skola.test → 192.168.100.1"

---

Aplikace

- běží v Docker kontejneru
- port: "8081"

Endpointy

- "/ping" – test dostupnosti (vrací "pong")
- "/status" – stav aplikace
- "/ai" – zpracování finančního dotazu

---

Použité technologie

- Ubuntu Server
- Docker + Docker Compose
- Python (Flask)
- Redis
- DNS + DHCP
- Ollama (LLM model)

---

Spuštění projektu

Projekt se spouští na serveru (Ubuntu Server), kde je nainstalovaný Docker.

1. Přesun do složky projektu:

cd ~/projekt

2. Spuštění aplikace:

docker compose up -d --build

Aplikace je poté dostupná v síti na adrese:
http://maksym.skola.test:8081

---

Testování

DNS

nslookup maksym.skola.test

Konektivita

ping maksym.skola.test

API test

curl http://maksym.skola.test:8081/ping
curl http://maksym.skola.test:8081/status

---

Test AI

curl -X POST http://maksym.skola.test:8081/ai \
-H "Content-Type: application/json" \
-d '{"prompt":"Mám 500 Kč a koupím si věc za 320 Kč. Kolik mi zbyde?"}'

---

Video

Odkaz na demonstrační video:
https://drive.google.com/file/d/1tlWjFGYoi0fWXyXMQ2dhSfpI0si2BEMA/view?usp=sharing

---

Vysvětlení fungování

DNS server překládá doménu "maksym.skola.test" na IP adresu "192.168.100.1".

Na této adrese běží Docker aplikace na portu "8081", která přijímá požadavky uživatele.
Požadavek je zpracován aplikací a předán AI modelu (Ollama), který vrátí odpověď zpět uživateli.

---

Autor

Maksym Bondar – projekt vytvořen v rámci výuky
