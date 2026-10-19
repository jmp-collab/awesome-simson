// Website-Check: ruft eine Startseite auf und bewertet die wichtigsten Punkte.
// Optional: Umgebungsvariable PSI_API_KEY für Google PageSpeed Insights (mobile Leistung).
const PRIVATE = /^(localhost|127\.|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|169\.254\.|0\.|\[?::1\]?$|.*\.local$|.*\.internal$)/i;

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

async function timed(url, opts = {}) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), opts.timeout || 9000);
  const start = Date.now();
  try {
    const r = await fetch(url, { redirect: opts.redirect || "follow", signal: ctrl.signal, headers: { "user-agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Mobile Safari/537.36 SaarseitenCheck/1.0", "accept-language": "de-DE,de;q=0.9" } });
    return { r, ms: Date.now() - start };
  } finally { clearTimeout(t); }
}

export default async (req) => {
  let raw = (new URL(req.url).searchParams.get("url") || "").trim();
  if (!raw) return json({ error: "Bitte eine Adresse eingeben." }, 400);
  if (!/^https?:\/\//i.test(raw)) raw = "https://" + raw;
  let u;
  try { u = new URL(raw); } catch { return json({ error: "Das sieht nicht nach einer Website-Adresse aus." }, 400); }
  const host = u.hostname.toLowerCase();
  if (!host.includes(".") || PRIVATE.test(host) || /^\d+\.\d+\.\d+\.\d+$/.test(host) || host.includes(":")) return json({ error: "Diese Adresse kann ich nicht prüfen." }, 400);

  const checks = [];
  const add = (label, state, detail) => checks.push({ label, state, detail });

  // HTTPS
  let res, ms, final = "", httpsOk = false;
  try { ({ r: res, ms } = await timed(`https://${host}${u.pathname}`)); final = res.url; httpsOk = res.ok && final.startsWith("https://"); } catch { /* fällt auf http zurück */ }
  if (!httpsOk) {
    try { ({ r: res, ms } = await timed(`http://${host}${u.pathname}`)); final = res.url; } catch { return json({ error: "Die Seite hat nicht geantwortet. Stimmt die Adresse?" }, 200); }
  }
  add("Verschlüsselt (HTTPS)", httpsOk ? "ok" : "bad", httpsOk ? "Die Seite lädt verschlüsselt. Browser zeigen kein Warnschild." : "Die Seite lädt nicht verschlüsselt. Chrome und Safari zeigen Besuchern den Hinweis 'Nicht sicher'.");

  // Weiterleitung http -> https
  if (httpsOk) {
    try {
      const { r } = await timed(`http://${host}/`, { redirect: "manual", timeout: 5000 });
      const loc = r.headers.get("location") || "";
      const ok = r.status >= 300 && r.status < 400 && loc.startsWith("https://");
      add("Weiterleitung auf HTTPS", ok ? "ok" : "warn", ok ? "Wer die alte Adresse ohne https eintippt, landet automatisch auf der sicheren Seite." : "Die Adresse ohne https leitet nicht sauber weiter. Manche Besucher sehen die unsichere Version.");
    } catch { /* ignorieren */ }
  }

  const html = (await res.text()).slice(0, 600000);
  const low = html.toLowerCase();
  const kb = Math.round(html.length / 1024);

  const vp = /<meta[^>]+name=["']?viewport["']?[^>]*>/i.exec(html);
  const vpOk = vp && /width\s*=\s*device-width/i.test(vp[0]);
  const fixed = /<(table|div|body|center)[^>]*width\s*[:=]\s*["']?\s*(?:[89]\d\d|1\d{3})(?:px)?/i.test(html) || /<style[\s\S]*?(?:#|\.)(?:wrap|container|page|main|site)[^{]*\{[^}]*\bwidth\s*:\s*(?:[89]\d\d|1\d{3})px/i.test(html);
  if (vpOk && fixed) add("Auf dem Handy angepasst", "warn", "Die Seite meldet sich als handytauglich, nutzt aber feste Breiten ab 800 Pixel. Auf dem Handy müssen Besucher oft trotzdem zoomen.");
  else add("Auf dem Handy angepasst", vpOk ? "ok" : "bad", vpOk ? "Die Seite meldet dem Handy, dass sie sich an die Bildschirmbreite anpasst." : "Die Seite ist nicht für Smartphones eingerichtet. Besucher müssen zoomen und seitlich wischen.");

  const title = (/<title[^>]*>([^<]*)<\/title>/i.exec(html) || [])[1]?.trim() || "";
  const desc = (/<meta[^>]+name=["']description["'][^>]+content=["']([^"']*)/i.exec(html) || [])[1]?.trim() || "";
  add("Titel und Beschreibung für Google", title && desc ? "ok" : title ? "warn" : "bad",
    title && desc ? `Titel: "${title.slice(0, 70)}"` : title ? "Ein Titel ist da, aber keine Beschreibung. Google wählt dann selbst einen Textausschnitt." : "Die Seite hat keinen Titel. In Google erscheint dann nur die Adresse.");

  const ld = /application\/ld\+json/i.test(html) && /(localbusiness|restaurant|store|dentist|physician|pharmacy|homeandconstructionbusiness|autorepair|beautysalon|hotel|organization)/i.test(html);
  add("Adresse und Öffnungszeiten für Google", ld ? "ok" : "warn", ld ? "Strukturierte Daten zum Betrieb sind vorhanden." : "Google bekommt Adresse, Öffnungszeiten und Branche nicht in maschinenlesbarer Form.");

  const tel = /href=["']tel:/i.test(html);
  add("Telefonnummer anklickbar", tel ? "ok" : "warn", tel ? "Besucher können auf dem Handy direkt anrufen." : "Auf der Startseite ist keine anklickbare Telefonnummer. Auf dem Handy heißt das: abschreiben.");

  const social = /(instagram\.com|facebook\.com)/i.test(low);
  add("Instagram oder Facebook verlinkt", social ? "ok" : "warn", social ? "Ihre Social-Media-Profile sind verlinkt." : "Weder Instagram noch Facebook sind verlinkt.");

  const imp = /impressum/i.test(low);
  add("Impressum verlinkt", imp ? "ok" : "bad", imp ? "Ein Impressum ist verlinkt." : "Auf der Startseite ist kein Impressum verlinkt. Das ist Pflicht und ein häufiger Abmahngrund.");

  const years = [...low.matchAll(/(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-\u2013]\s*)?(\d{4})/g)].map((m) => +m[1]);
  const yr = years.length ? Math.max(...years) : 0;
  if (yr) add("Zuletzt sichtbar aktualisiert", yr >= new Date().getFullYear() - 1 ? "ok" : "warn", `Im Fuß der Seite steht ${yr}.`);

  // Ladezeit
  let speed = null;
  if (process.env.PSI_API_KEY) {
    try {
      const api = `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(final)}&strategy=mobile&category=performance&key=${process.env.PSI_API_KEY}`;
      const { r } = await timed(api, { timeout: 25000 });
      const d = await r.json();
      const score = Math.round((d.lighthouseResult?.categories?.performance?.score || 0) * 100);
      const lcp = d.lighthouseResult?.audits?.["largest-contentful-paint"]?.displayValue || "";
      speed = { score, lcp };
      add("Ladezeit auf dem Handy (Google)", score >= 80 ? "ok" : score >= 50 ? "warn" : "bad", `Google bewertet die mobile Leistung mit ${score} von 100. Hauptinhalt sichtbar nach ${lcp}.`);
    } catch { /* ohne PSI weiter */ }
  }
  if (!speed) add("Antwortzeit des Servers", ms < 800 ? "ok" : ms < 2000 ? "warn" : "bad", `Der Server hat nach ${(ms / 1000).toFixed(1).replace(".", ",")} Sekunden geantwortet, die Startseite ist ${kb} KB groß (nur HTML).`);

  return json({ host, final, checks });
};

export const config = { path: "/api/check" };
