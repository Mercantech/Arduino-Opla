const state = {
  devices: [],
  healthOk: false,
  view: "home",
  samdId: null,
};

function $(sel) {
  return document.querySelector(sel);
}

function fmtWhen(iso) {
  try {
    return new Date(iso).toLocaleString("da-DK", {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return iso || "—";
  }
}

function shortId(id) {
  if (!id) return "—";
  if (id.length <= 16) return id;
  return id.slice(0, 8) + "…" + id.slice(-8);
}

function parseHash() {
  const h = location.hash.replace(/^#\/?/, "");
  if (h.startsWith("device/")) {
    state.view = "device";
    state.samdId = decodeURIComponent(h.slice(7));
  } else {
    state.view = "home";
    state.samdId = null;
  }
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(url + " " + res.status);
  return res.json();
}

async function refresh() {
  try {
    await fetchJson("/api/health");
    state.healthOk = true;
  } catch {
    state.healthOk = false;
  }
  try {
    state.devices = await fetchJson("/api/devices");
  } catch {
    state.devices = [];
  }
  render();
}

function renderHealth() {
  const el = $("#health");
  if (!el) return;
  el.innerHTML = state.healthOk
    ? `<span class="dot ok"></span> API online`
    : `<span class="dot bad"></span> API utilgængelig`;
}

function renderHome() {
  const root = $("#app");
  const devices = state.devices || [];
  const okCount = devices.filter((d) => d.last_passed === true).length;
  const failCount = devices.filter((d) => d.last_passed === false).length;

  root.innerHTML = `
    <header class="hero">
      <p class="status-pill" id="health"></p>
      <h1 class="hero-brand">Opla</h1>
      <p class="hero-line">Hardware-test og enhedsregistrering for Arduino Opla. Fuld historik pr. SAMD-ID.</p>
      <div class="hero-actions">
        <button class="btn btn-primary" type="button" id="btn-refresh">Opdater liste</button>
        <a class="btn btn-ghost" href="https://docs.arduino.cc/tutorials/mkr-iot-carrier/mkr-iot-carrier-01-technical-reference" target="_blank" rel="noreferrer">Carrier docs</a>
      </div>
    </header>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Enheder</h2>
          <p>${devices.length} registreret · ${okCount} senest OK · ${failCount} senest fejl</p>
        </div>
      </div>
      <div class="device-list" id="device-list"></div>
    </section>
  `;

  renderHealth();
  $("#btn-refresh")?.addEventListener("click", () => refresh());

  const list = $("#device-list");
  if (!devices.length) {
    list.innerHTML = `<div class="empty">Ingen enheder endnu. Kør HardwareTest på et board — det registrerer sig selv.</div>`;
    return;
  }

  list.innerHTML = devices
    .map((d, i) => {
      const badge =
        d.last_passed === true
          ? `<span class="badge ok">Senest OK</span>`
          : d.last_passed === false
            ? `<span class="badge bad">Senest fejl</span>`
            : `<span class="badge muted">Ingen tests</span>`;
      return `
        <button class="device-row" type="button" data-id="${d.samd_id}" style="animation-delay:${i * 0.04}s">
          <div>
            <h3>${d.label || "Arduino Opla"}</h3>
            <div class="device-meta">${d.samd_id}</div>
            <div class="device-meta">${d.mac || "—"} · ${d.ecc_serial || "—"}</div>
          </div>
          <div class="device-side">
            ${badge}
            <span class="device-meta">${d.test_count || 0} tests · ${fmtWhen(d.updated_at)}</span>
          </div>
        </button>`;
    })
    .join("");

  list.querySelectorAll("[data-id]").forEach((btn) => {
    btn.addEventListener("click", () => {
      location.hash = "#/device/" + encodeURIComponent(btn.dataset.id);
    });
  });
}

function renderDevice() {
  const root = $("#app");
  const d = state.devices.find((x) => x.samd_id === state.samdId);
  if (!d) {
    root.innerHTML = `
      <button class="back" type="button" id="btn-back">← Tilbage</button>
      <div class="empty">Enhed ikke fundet. <button class="btn btn-ghost" type="button" id="btn-reload">Hent igen</button></div>`;
    $("#btn-back")?.addEventListener("click", () => (location.hash = "#/"));
    $("#btn-reload")?.addEventListener("click", () => refresh());
    return;
  }

  const tests = d.tests || [];
  const passRuns = tests.filter((t) => t.passed).length;

  root.innerHTML = `
    <button class="back" type="button" id="btn-back">← Alle enheder</button>
    <header class="detail-hero">
      <p class="status-pill" id="health"></p>
      <h1>${d.label || "Arduino Opla"}</h1>
      <div class="detail-id">${d.samd_id}</div>
    </header>

    <div class="stats">
      <div class="stat"><b>${tests.length}</b><span>Testkørsler</span></div>
      <div class="stat"><b>${passRuns}</b><span>Bestået</span></div>
      <div class="stat"><b>${tests.length - passRuns}</b><span>Med fejl</span></div>
    </div>

    <dl class="idents">
      <div class="ident"><dt>SAMD</dt><dd>${d.samd_id}</dd></div>
      <div class="ident"><dt>WiFi MAC</dt><dd>${d.mac || "—"}</dd></div>
      <div class="ident"><dt>ECCX08</dt><dd>${d.ecc_serial || "—"}</dd></div>
      <div class="ident"><dt>Først set</dt><dd>${fmtWhen(d.created_at)}</dd></div>
      <div class="ident"><dt>Opdateret</dt><dd>${fmtWhen(d.updated_at)}</dd></div>
    </dl>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Testhistorik</h2>
          <p>Nyeste foerst · klik for fulde detaljer</p>
        </div>
      </div>
      <div class="timeline" id="timeline"></div>
    </section>
  `;

  renderHealth();
  $("#btn-back")?.addEventListener("click", () => (location.hash = "#/"));

  const timeline = $("#timeline");
  if (!tests.length) {
    timeline.innerHTML = `<div class="empty">Ingen tests endnu</div>`;
    return;
  }

  timeline.innerHTML = tests
    .map((t, idx) => {
      const report = t.report || {};
      const items = Array.isArray(report.tests) ? report.tests : [];
      const itemsHtml = items.length
        ? `<div class="test-grid">${items
            .map((it) => {
              const badge = it.skipped
                ? `<span class="badge muted">Skip</span>`
                : it.ok
                  ? `<span class="badge ok">OK</span>`
                  : `<span class="badge bad">Fejl</span>`;
              return `<div class="test-item">${badge}<div>
                <div class="name">${it.name || "Test"}</div>
                ${it.note ? `<div class="note">${it.note}</div>` : ""}
              </div></div>`;
            })
            .join("")}</div>`
        : `<p class="run-sub">Ingen del-resultater i denne kørsel (ældre format).</p>`;

      const metaBits = [];
      if (typeof report.sound_enabled === "boolean") {
        metaBits.push(report.sound_enabled ? "Lyd til" : "Lyd fra");
      }
      if (report.firmware) metaBits.push(report.firmware);
      if (report.wifi_ssid) metaBits.push("WiFi " + report.wifi_ssid);

      return `
        <article class="run" data-idx="${idx}" style="animation-delay:${idx * 0.03}s">
          <button class="run-summary" type="button">
            <span class="run-dot ${t.passed ? "" : "bad"}"></span>
            <div>
              <div class="run-when">${fmtWhen(t.created_at)}</div>
              <div class="run-sub">${t.passed_count} ok · ${t.failed_count} fejl${metaBits.length ? " · " + metaBits.join(" · ") : ""}</div>
            </div>
            <span class="badge ${t.passed ? "ok" : "bad"}">${t.passed ? "Bestået" : "Fejl"}</span>
          </button>
          <div class="run-body">
            ${itemsHtml}
            <details>
              <summary>Rå JSON</summary>
              <pre class="raw">${escapeHtml(JSON.stringify(t.report || t.details || t, null, 2))}</pre>
            </details>
          </div>
        </article>`;
    })
    .join("");

  timeline.querySelectorAll(".run").forEach((run) => {
    run.querySelector(".run-summary")?.addEventListener("click", () => {
      run.classList.toggle("open");
    });
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function render() {
  parseHash();
  if (state.view === "device") renderDevice();
  else renderHome();
}

window.addEventListener("hashchange", () => render());
refresh();
setInterval(refresh, 20000);
