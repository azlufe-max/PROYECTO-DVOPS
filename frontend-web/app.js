/**
 * app.js – Lógica del cliente Guest-Pass Frontend
 * API base: http://localhost:8000
 * Spec: SPEC_TECNICA.md § 2
 */

const API_BASE = "http://localhost:8000";

// ── DOM refs ────────────────────────────────────────────────
const form        = document.getElementById("checkin-form");
const submitBtn   = document.getElementById("submit-btn");
const btnText     = submitBtn.querySelector(".btn-text");
const btnSpinner  = submitBtn.querySelector(".btn-spinner");
const toast       = document.getElementById("toast");
const recordsBody = document.getElementById("records-body");
const recordCount = document.getElementById("record-count");
const refreshBtn  = document.getElementById("refresh-btn");
const statusDot   = document.getElementById("status-dot");
const statusLabel = document.getElementById("status-label");

// ── Health check ────────────────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(4000) });
    if (res.ok) {
      setStatus("ok", "API conectada");
    } else {
      setStatus("error", "API no disponible");
    }
  } catch {
    setStatus("error", "Sin conexión");
  }
}

function setStatus(state, label) {
  statusDot.className = `dot dot--${state}`;
  statusLabel.textContent = label;
}

// ── Fetch records ────────────────────────────────────────────
async function fetchRecords() {
  setRefreshLoading(true);
  try {
    const res = await fetch(`${API_BASE}/api/v1/checkins`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderTable(data);
  } catch (err) {
    renderTableError(err.message);
  } finally {
    setRefreshLoading(false);
  }
}

function setRefreshLoading(loading) {
  refreshBtn.disabled = loading;
  refreshBtn.style.opacity = loading ? ".5" : "1";
}

function renderTable(records) {
  if (!records.length) {
    recordsBody.innerHTML = `
      <tr class="empty-row">
        <td colspan="6">
          <div class="empty-state">
            <span class="empty-icon">📭</span>
            <p>No hay registros aún. ¡Registra el primer visitante!</p>
          </div>
        </td>
      </tr>`;
    recordCount.textContent = "Sin registros";
    return;
  }

  recordCount.textContent = `${records.length} registro${records.length !== 1 ? "s" : ""}`;

  recordsBody.innerHTML = records.map((r, i) => `
    <tr class="row-new" style="animation-delay:${i * 30}ms">
      <td>${r.id}</td>
      <td style="color:var(--text-primary);font-weight:500">${escHtml(r.nombre)}</td>
      <td>${r.empresa ? escHtml(r.empresa) : '<span style="color:var(--text-muted)">—</span>'}</td>
      <td>${r.motivo ? escHtml(r.motivo) : '<span style="color:var(--text-muted)">—</span>'}</td>
      <td><span class="badge badge--${r.origen}">${r.origen}</span></td>
      <td style="white-space:nowrap">${formatDate(r.fecha_registro)}</td>
    </tr>
  `).join("");
}

function renderTableError(msg) {
  recordsBody.innerHTML = `
    <tr class="empty-row">
      <td colspan="6">
        <div class="empty-state">
          <span class="empty-icon">⚠️</span>
          <p>Error al cargar registros: ${escHtml(msg)}</p>
        </div>
      </td>
    </tr>`;
  recordCount.textContent = "Error al cargar";
}

// ── Form submit ──────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!validateForm()) return;

  const payload = {
    nombre:    document.getElementById("nombre").value.trim(),
    empresa:   document.getElementById("empresa").value.trim() || null,
    motivo:    document.getElementById("motivo").value.trim()  || null,
    origen:    "web",
    timestamp: new Date().toISOString(),
  };

  setSubmitLoading(true);
  hideToast();

  try {
    const res = await fetch(`${API_BASE}/api/v1/checkin`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    showToast("success", `✅ Visitante "${payload.nombre}" registrado correctamente.`);
    form.reset();
    await fetchRecords();

  } catch (err) {
    showToast("error", `❌ Error: ${err.message}`);
  } finally {
    setSubmitLoading(false);
  }
});

// ── Form validation ──────────────────────────────────────────
function validateForm() {
  let valid = true;
  const nombre = document.getElementById("nombre");
  const errNombre = document.getElementById("err-nombre");

  nombre.classList.remove("invalid");
  errNombre.textContent = "";

  if (!nombre.value.trim()) {
    nombre.classList.add("invalid");
    errNombre.textContent = "El nombre es obligatorio.";
    nombre.focus();
    valid = false;
  }
  return valid;
}

// ── UI helpers ───────────────────────────────────────────────
function setSubmitLoading(loading) {
  submitBtn.disabled = loading;
  btnText.classList.toggle("hidden", loading);
  btnSpinner.classList.toggle("hidden", !loading);
}

let toastTimer;
function showToast(type, msg) {
  clearTimeout(toastTimer);
  toast.className = `toast toast--${type}`;
  toast.textContent = msg;
  toast.classList.remove("hidden");
  toastTimer = setTimeout(hideToast, 6000);
}
function hideToast() {
  toast.classList.add("hidden");
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatDate(iso) {
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleString("es-MX", {
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });
}

// ── Refresh button ───────────────────────────────────────────
refreshBtn.addEventListener("click", fetchRecords);

// ── Init ─────────────────────────────────────────────────────
(async () => {
  await checkHealth();
  await fetchRecords();
})();
