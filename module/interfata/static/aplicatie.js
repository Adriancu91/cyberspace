// Pagina de chat a interfeței Cyberspace v0. Fără biblioteci externe.
// Regulă: orice text venit de la om sau de la model se pune în pagină DOAR cu textContent, niciodată ca HTML,
// ca un mesaj de felul <script>...</script> să se vadă ca text și să nu se execute.
"use strict";

const el = (id) => document.getElementById(id);
let conversatieCurenta = null;   // numărul conversației deschise; null = una nouă, creată la primul mesaj
let lungimeMaxima = 2000;

function element(tip, clasa, text) {
  const e = document.createElement(tip);
  if (clasa) e.className = clasa;
  if (text !== undefined) e.textContent = text;
  return e;
}

async function cere(cale, corp) {
  const optiuni = corp === undefined ? {} : {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corp),
  };
  const raspuns = await fetch(cale, optiuni);
  let date = null;
  try { date = await raspuns.json(); } catch (e) { /* răspuns fără JSON */ }
  if (!raspuns.ok) throw new Error((date && date.eroare) || ("Eroare " + raspuns.status));
  return date;
}

function anunta(text) { el("anunt").textContent = text || ""; }

function ora(text) {
  const d = new Date(text);
  return isNaN(d) ? "" : d.toLocaleString("ro-RO", { dateStyle: "short", timeStyle: "short" });
}

function arataMesaj(m) {
  const cutie = element("article", "mesaj " + (m.rol === "om" ? "om" : "creier"));
  let antet = m.autor + " · " + ora(m.creat);
  if (typeof m.secunde === "number") antet += " · " + m.secunde.toLocaleString("ro-RO") + " s";
  cutie.appendChild(element("p", "autor", antet));
  cutie.appendChild(element("p", "text", m.text));
  el("mesaje").appendChild(cutie);
  cutie.scrollIntoView({ block: "end" });
}

function golesteMesajele() { el("mesaje").replaceChildren(); }

async function incarcaConversatiile() {
  const date = await cere("/api/conversatii");
  const lista = el("conversatii");
  lista.replaceChildren();
  for (const c of date.conversatii) {
    const buton = element("button", c.id === conversatieCurenta ? "aleasa" : "", c.titlu);
    buton.type = "button";
    buton.title = ora(c.creata) + " · " + c.mesaje + " mesaje";
    buton.addEventListener("click", () => deschide(c.id));
    const rand = element("li");
    rand.appendChild(buton);
    lista.appendChild(rand);
  }
}

async function deschide(numar) {
  try {
    const date = await cere("/api/conversatii/" + numar);
    conversatieCurenta = numar;
    golesteMesajele();
    date.mesaje.forEach(arataMesaj);
    anunta("");
    await incarcaConversatiile();
  } catch (e) { anunta(e.message); }
}

async function trimite(eveniment) {
  eveniment.preventDefault();
  const camp = el("text");
  const text = camp.value;
  if (!text.trim()) return;
  if (text.length > lungimeMaxima) {
    anunta("Mesajul are " + text.length + " caractere; cel mult " + lungimeMaxima + ".");
    return;
  }
  el("trimite").disabled = true;
  anunta("Kronos se gândește… (prima întrebare durează mai mult: se încarcă modelul)");
  try {
    const date = await cere("/api/mesaj", { conversatie: conversatieCurenta, text: text });
    conversatieCurenta = date.conversatie;
    camp.value = "";
    arataMesaj(date.intrebare);
    if (date.raspuns) { arataMesaj(date.raspuns); anunta(""); } else { anunta(date.eroare); }
    await incarcaConversatiile();
  } catch (e) {
    anunta("Mesajul nu a plecat: " + e.message);
  } finally {
    el("trimite").disabled = false;
    camp.focus();
  }
}

async function incarcaModulele() {
  const date = await cere("/api/module");
  el("configurare").textContent = date.configurare ? "(configurarea „" + date.configurare + "”)" : "";
  const zona = el("module");
  zona.replaceChildren();
  for (const m of date.module) {
    const buton = element("button", m.eroare ? "modul stricat" : "modul");
    buton.type = "button";
    buton.appendChild(element("span", "port", m.port));
    buton.appendChild(element("span", "nume", m.nume || "?"));
    buton.addEventListener("click", () => {
      const detalii = el("detalii-modul");
      detalii.hidden = false;
      detalii.textContent = "Portul „" + m.port + "”: modulul " + (m.nume_afisat || m.nume || "necunoscut")
        + (m.versiune ? ", versiunea " + m.versiune : "") + ". Clasa: " + m.cale + "."
        + (m.descriere ? " " + m.descriere : "") + (m.eroare ? " Problemă: " + m.eroare : "");
    });
    zona.appendChild(buton);
  }
}

async function porneste() {
  el("formular").addEventListener("submit", trimite);
  el("text").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) el("formular").requestSubmit();
  });
  el("conversatie-noua").addEventListener("click", () => {
    conversatieCurenta = null;
    golesteMesajele();
    anunta("");
    incarcaConversatiile().catch((e) => anunta(e.message));
    el("text").focus();
  });
  try {
    const stare = await cere("/api/stare");
    el("cine").textContent = "Răspunde: " + stare.creier;
    lungimeMaxima = stare.lungime_maxima_mesaj;
    await incarcaModulele();
    await incarcaConversatiile();
  } catch (e) { anunta("Nu pot vorbi cu serverul: " + e.message); }
}

porneste();
