"""Romanian Language Core (RLC) — motorul lingvistic simbolic pentru limba română.

Modul al platformei Cyberspace, independent de nucleul Kronos. Totul e explicit, inspectabil și verificabil:
lexicon cu identificatori stabili, forme cu trăsături și proveniență, reguli de acord, sensuri și concepte.

Folosire rapidă:
    from module.limba_romana import Motor
    motor = Motor()                      # deschide baza din _baza/limba_romana.sqlite
    rezultat = motor.analizeaza("Copiii frumoși au plecat la școală.")
    probleme = motor.verifica_text("Copii frumoasă a plecat.")
"""

VERSIUNE = "0.1.0"

__all__ = ["VERSIUNE", "Motor"]


def __getattr__(nume: str):
    if nume == "Motor":
        from .motor import Motor
        return Motor
    raise AttributeError(nume)
