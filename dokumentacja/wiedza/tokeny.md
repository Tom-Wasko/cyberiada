# Tokeny, koszt i limity

Sprawdzone: 2026-11-22

## Z czego składa się koszt
- Płacisz za cztery rodzaje tokenów: wejście, wyjście, zapis do cache i odczyt z cache. Claude Code pokazuje je w `/usage`
  (np. „input, output, cache read, cache write”). Źródło: https://code.claude.com/docs/en/costs
- Cache to zapamiętany początek rozmowy, który przy kolejnej turze kosztuje dużo mniej. Zapis na 5 min = 1,25× ceny wejścia,
  zapis na 1 h = 2×, odczyt = 0,1× (Opus 5.5 i Sonnet 5.5: 0,05×; Fable 5.x: 0,025×).
  Źródło: https://platform.claude.com/docs/en/about-claude/pricing
- Czas życia cache: domyślnie 5 minut, każde użycie odnawia go bez dopłaty; dłuższy (1 h) trzeba wybrać osobno.
  Przerwa dłuższa niż 5 min = kolejna tura płaci znów za zapis. Krótszy prompt niż minimum (512 tokenów dla modeli 5.x) nie wchodzi do cache.
  Źródło: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Wyjście kosztuje 5× wejście (wynika z tabeli cen, strona tego nie mówi wprost). Tokeny „myślenia” liczą się jak wyjście.
  Źródła: https://platform.claude.com/docs/en/about-claude/pricing , https://code.claude.com/docs/en/costs

## Modele (cena za 1 mln tokenów, wejście / wyjście, USD)
- Fable 5.2: 8 / 40. Opus 5.5: 4 / 20. Sonnet 5.5: 2 / 10. Haiku 5.5: 0,10 / 0,50 (do 100 tys. tokenów promptu; powyżej 0,50 / 2,50).
  Źródło: https://platform.claude.com/docs/en/about-claude/pricing
- Czyli względem Sonneta: Opus 2×, Fable 4×, Haiku 0,05×.
- Aliasy w Claude Code: `opus` → Opus 5.5, `sonnet` → Sonnet 5.5, `haiku` → Haiku 5.5.
  Źródło: https://code.claude.com/docs/en/model-config

## Limity planu
- Plany płatne mają limit sesji, który odnawia się co 5 godzin (okno liczone od pierwszej wiadomości), oraz limit tygodniowy
  (wspólny dla modeli; niektóre plany mają osobny tygodniowy dla Fable). Claude Code, claude.ai i aplikacja liczą się do jednego limitu.
  Zużycie zależy od długości rozmowy, modelu i poziomu effort. Konkretnych liczb (wiadomości, tokeny) strona nie podaje.
  Źródło: https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work
- Procent limitu widać w statusline (`rate_limits.five_hour`, `seven_day`): https://code.claude.com/docs/en/statusline (test T6).

## Co zjada kontekst
- Na starcie: prompt systemowy, CLAUDE.md, pamięć, opisy skilli, nazwy narzędzi MCP. Pełne definicje MCP są odroczone
  (wchodzą dopiero po użyciu narzędzia). Źródła: https://code.claude.com/docs/en/context-window , https://code.claude.com/docs/en/costs
- Podagent ma własne okno kontekstu, ale jego zużycie i tak liczy się do limitu. Źródła: ten sam kontekst i koszty.
  Na tym komputerze: start zwiadowcy ok. 6 tys. tokenów, sesji `--bg` ok. 48 tys. (`testy.md`, T5).

## Jak oszczędzać
- CLAUDE.md poniżej ok. 200 linii; rzadkie instrukcje do skilli (ładują się na żądanie).
- `/clear` między zadaniami, `/compact` w długich; tańszy model do prostych rzeczy (Sonnet, Haiku dla podagentów); niższy effort.
- Hooki mogą skracać długie wyniki poleceń. Źródło dla wszystkich punktów: https://code.claude.com/docs/en/costs

## Czy wagi w `narzedzia/zuzycie.py` zgadzają się ze źródłami?
Częściowo.
- Wyjście 5×: **tak**. Mnożniki Opus 2,0 i Haiku 0,05: **tak** (względem Sonneta 5.5).
- Fable 2,0: **nie**: z cen wychodzi 4,0 (8 vs 2 za wejście). Poprawić.
- Zapis cache 2,0: to cena zapisu 1 h; zapis 5 min to 1,25. Domyślny w Claude Code jest 5 min, więc 2,0 zawyża (nie sprawdzono, który
  czas Claude Code faktycznie używa: do sprawdzenia w logach).
- Odczyt cache 0,1: **tak** dla starszych modeli; dla Opus 5.5 i Sonnet 5.5 jest 0,05, dla Fable 0,025. Zawyża ok. 2×.
- Haiku 5.5 powyżej 100 tys. tokenów promptu kosztuje 5× więcej (mnożnik 0,25): w wadze go nie ma.
Źródło wszystkich liczb: https://platform.claude.com/docs/en/about-claude/pricing
