# Executantul: descărcările aprobate de Adrian (varianta b)

*Scris de Claude Code pe 19 octombrie 2026, la 21:00.*

## Ce ai hotărât

„(b) da: executantul are voie la o descărcare doar dacă sarcina are „aprobat de: Adrian” și pomenește anume
descărcarea (cum e S2). Restul rămâne interzis.” Sarcina Windows o înregistrezi tu la workstation.

## Ce am schimbat

Doar instrucțiunea executantului (`unelte/executant_coada.txt`), la „Ce ai voie”. O descărcare e permisă **doar**
dacă sunt îndeplinite toate trei:

- sarcina are „aprobat de: Adrian”;
- „ce faci” pomenește anume descărcarea;
- descărcarea se face doar cu unealta scrisă acolo (la S2:
  `python -m module.limba_romana.importatoare.descarca_surse`).

În raport, executantul spune ce s-a descărcat și cât.

O descărcare aprobată doar de supraveghetor, sau care nu e pomenită anume, rămâne interzisă: sarcina trece pe
`oprit`, cu motivul „cere aprobarea lui Adrian: descărcare”.

Neschimbate:

- `curl`, `wget` și `pip` rămân blocate în setările executantului.
- Sunt interzise în continuare `kronos/`, examenul, jurnalul, setările CONTINUUM și sarcinile Windows.

**Testele:** 745 trecute, 1 sărit.

## Ce urmează

- După ce înregistrezi „Kronos executant coada” (comanda e în
  `docs/rapoarte/2026-10-19_2040_executantul_cascadei_proba.md`), executantul se uită la coadă la fiecare 30 de
  minute.
  - **Noaptea:** doar urmărește S1 (noaptea 10).
  - **După raportul de la 07:40:** pune S1 `gata`.
  - **De la 08:00:** ia S2 (pe procesor): merge-ul în `main`, cu testele care se sar fără bază, descărcarea surselor,
    construirea bazei și măsurarea.
- **Dacă n-ai înregistrat sarcina până mâine dimineață,** S2 nu pornește singură. Executantul nu rulează fără
  sarcina Windows.

## Ce aștept de la tine

Doar înregistrarea sarcinii Windows, când ajungi la workstation.
