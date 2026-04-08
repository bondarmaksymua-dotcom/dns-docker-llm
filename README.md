# README.md

## Projekt: Finanční AI asistent (DNS + Docker + LLM)

## Co projekt dělá
Tento projekt vytváří síťovou službu, která umožňuje uživatelům posílat finanční dotazy na AI model.
Aplikace běží v Docker kontejneru a je dostupná přes vlastní doménu v lokální síti.

## K čemu je projekt určen
Projekt slouží jako finanční pomocník, který odpovídá na jednoduché otázky týkající se peněz (např. výpočty zůstatku).
Zároveň demonstruje propojení DNS, DHCP a Docker aplikace v praxi.

## Pro koho je určen
Aplikaci mohou používat uživatelé v lokální síti (např. spolužáci).
Uživatel zadá dotaz a AI vrátí krátkou odpověď.

## Síťová konfigurace

- Server IP: 192.168.100.1/24
- Klient získává IP přes DHCP
- DNS:
  maksym.skola.test → 192.168.100.1

## Aplikace

- Běží v Docker kontejneru
- Port: 8081

### Endpointy:
- /ping – test dostupnosti
- /status – stav aplikace
- /ai – finanční dotazy na AI

## Technologie

- Ubuntu Server
- Docker + docker-compose
- Python + Flask
- DNS + DHCP
- Ollama (LLM model)

## Spuštění projektu

docker compose up -d --build

## Testování

### DNS:
nslookup maksym.skola.test

### Ping:
ping maksym.skola.test

### Aplikace:
curl http://maksym.skola.test:8081/ping
curl http://maksym.skola.test:8081/status

## Test AI

curl -X POST http://maksym.skola.test:8081/ai -H "Content-Type: application/json" -d '{"prompt":"Mám 500 Kč a koupím si věc za 320 Kč. Kolik mi zbyde?"}'

## Video

Odkaz na demonstrační video:
(https://drive.google.com/file/d/1tlWjFGYoi0fWXyXMQ2dhSfpI0si2BEMA/view?usp=sharing)

## Vysvětlení

DNS překládá doménu maksym.skola.test na IP adresu serveru 192.168.100.1.
Na této adrese běží Docker aplikace na portu 8081, která zpracuje požadavek a předá ho AI modelu (Ollama).
Model vrátí odpověď uživateli.
