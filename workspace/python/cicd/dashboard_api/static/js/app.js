'use strict';

// ── State ────────────────────────────────────────────────────────────────────
const State = {
  theme: localStorage.getItem('theme') || 'dark',
  section: 'overview',
  dateFilter: parseInt(localStorage.getItem('dateFilter')) || 30,
  ws: null,
  charts: {},
  refreshTimer: null,
  REFRESH_MS: 60000,
};

const PALETTE = ['#6366f1','#10b981','#ef4444','#3b82f6','#f59e0b','#a855f7','#f97316','#06b6d4'];

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return `rgba(${r},${g},${b},${alpha})`;
}

// ── Utilities ────────────────────────────────────────────────────────────────
function esc(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function fmtDur(secs) {
  if (!secs && secs !== 0) return '-';
  const s = Math.round(secs);
  if (s < 60) return s + 's';
  if (s < 3600) return Math.floor(s/60) + 'm ' + (s%60) + 's';
  return Math.floor(s/3600) + 'h ' + Math.floor((s%3600)/60) + 'm';
}

function fmtDate(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
}

function fmtDateShort(iso) {
  if (!iso) return '-';
  return new Date(iso).toLocaleDateString();
}

function userCell(name, avatarUrl) {
  if (!name) return '<span class="td-empty">—</span>';
  const img = avatarUrl
    ? `<img src="${esc(avatarUrl)}" class="user-avatar" alt="" onerror="this.style.display='none'">`
    : '';
  return `<span class="user-cell">${img}<span class="user-name">${esc(name)}</span></span>`;
}

function badge(status) {
  const s = (status || '').toLowerCase();
  return `<span class="badge badge-${esc(s)}">${esc(status || '-')}</span>`;
}

function showToast(msg, type) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show ' + (type || '');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 3500);
}

// ── Theme ────────────────────────────────────────────────────────────────────
function applyTheme() {
  document.documentElement.setAttribute('data-theme', State.theme);
  const btn = document.getElementById('theme-btn');
  if (btn) btn.textContent = State.theme === 'dark' ? '\u2600' : '\u263D';
}

function toggleTheme() {
  State.theme = State.theme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('theme', State.theme);
  applyTheme();
}

// ── Date Filter ──────────────────────────────────────────────────────────────
function setDateFilter(days) {
  State.dateFilter = days;
  localStorage.setItem('dateFilter', days);

  // Update filter button text
  const filterText = document.getElementById('filter-text');
  if (filterText) filterText.textContent = `Last ${days} Days`;

  // Update active state in menu
  document.querySelectorAll('#filter-menu a').forEach(a => {
    a.classList.toggle('active', parseInt(a.dataset.days) === days);
  });

  // Update labels in UI
  const ovLabel = document.getElementById('ov-label-days');
  if (ovLabel) ovLabel.textContent = `(${days}d)`;

  const statusLabel = document.getElementById('chart-status-label');
  if (statusLabel) statusLabel.textContent = `(${days}d)`;

  const mrLabel = document.getElementById('chart-mr-label');
  if (mrLabel) mrLabel.textContent = `(${days} days)`;

  // Reload current section with new filter
  if (SECTION_LOADERS[State.section]) SECTION_LOADERS[State.section]();
}

// ── Chart helpers ─────────────────────────────────────────────────────────────
function chartDefaults() {
  const isDark = State.theme === 'dark';
  return {
    gridColor: isDark ? 'rgba(42,48,80,0.8)' : 'rgba(216,223,240,0.8)',
    textColor: isDark ? '#5d6785' : '#8892b0',
  };
}

function makeDataset(label, data, color, opts) {
  return {
    label,
    data,
    borderColor: color,
    backgroundColor: opts && opts.fill ? hexToRgba(color, 0.15) : color,
    borderWidth: 2,
    tension: 0.35,
    pointRadius: 0,
    pointHoverRadius: 4,
    fill: opts && opts.fill ? true : false,
    ...((opts && opts.extra) || {}),
  };
}

function buildLineChart(id, labels, datasets, opts) {
  const el = document.getElementById(id);
  if (!el) return;
  if (State.charts[id]) State.charts[id].destroy();
  const { gridColor, textColor } = chartDefaults();
  State.charts[id] = new Chart(el, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { labels: { color: textColor, boxWidth: 12, font: { size: 12 } } },
        tooltip: { backgroundColor: '#1a1e2e', titleColor: '#e8edf8', bodyColor: '#99a3bc', borderColor: '#2a3050', borderWidth: 1 },
      },
      scales: {
        x: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 11 }, maxRotation: 0 } },
        y: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 11 } }, min: 0 },
      },
    },
  });
}

function buildDoughnutChart(id, labels, data, colors) {
  const el = document.getElementById(id);
  if (!el) return;
  if (State.charts[id]) State.charts[id].destroy();
  const { textColor } = chartDefaults();
  State.charts[id] = new Chart(el, {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0, hoverOffset: 6 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '62%',
      plugins: {
        legend: { position: 'right', labels: { color: textColor, boxWidth: 12, font: { size: 12 }, padding: 12 } },
        tooltip: { backgroundColor: '#1a1e2e', titleColor: '#e8edf8', bodyColor: '#99a3bc', borderColor: '#2a3050', borderWidth: 1 },
      },
    },
  });
}

function buildBarChart(id, labels, datasets, opts) {
  const el = document.getElementById(id);
  if (!el) return;
  if (State.charts[id]) State.charts[id].destroy();
  const { gridColor, textColor } = chartDefaults();
  const isHoriz = opts && opts.horizontal;
  State.charts[id] = new Chart(el, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: isHoriz ? 'y' : 'x',
      plugins: {
        legend: { display: datasets.length > 1, labels: { color: textColor, boxWidth: 12, font: { size: 12 } } },
        tooltip: { backgroundColor: '#1a1e2e', titleColor: '#e8edf8', bodyColor: '#99a3bc', borderColor: '#2a3050', borderWidth: 1 },
      },
      scales: {
        x: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 11 } } },
        y: { grid: { color: gridColor }, ticks: { color: textColor, font: { size: 11 } } },
      },
    },
  });
}

// ── WebSocket ─────────────────────────────────────────────────────────────────
function setWsStatus(state) {
  const dot = document.getElementById('ws-dot');
  const lbl = document.getElementById('ws-label');
  const map = { connected: ['connected','Live'], connecting: ['connecting','Connecting...'], error: ['error','Disconnected'] };
  const [cls, text] = map[state] || map.error;
  if (dot) { dot.className = 'ws-dot ' + cls; }
  if (lbl) { lbl.textContent = text; }
}

function connectWS() {
  setWsStatus('connecting');
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${proto}://${location.host}/ws/metrics`);
  State.ws = ws;

  ws.onopen = () => setWsStatus('connected');

  ws.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data);
      if (msg.type === 'metrics') updateOverviewCards(msg.data);
    } catch (_) {}
  };

  ws.onclose = () => { setWsStatus('error'); setTimeout(connectWS, 4000); };
  ws.onerror = () => setWsStatus('error');
}

// ── Shared table renderers ────────────────────────────────────────────────────
function renderBranchTable(tbodyId, rows) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  if (!rows.length) { tbody.innerHTML = '<tr class="loading-row"><td colspan="6">No branches found</td></tr>'; return; }
  tbody.innerHTML = rows.map(b => {
    const sha = b.pipeline_url
      ? `<a href="${esc(b.pipeline_url)}" target="_blank" class="td-mono">${esc(b.commit_sha)}</a>`
      : `<span class="td-mono">${esc(b.commit_sha)}</span>`;
    const pipelineBadge = b.pipeline_status ? badge(b.pipeline_status) : '<span class="td-empty">—</span>';
    return `
    <tr>
      <td class="td-main">${esc(b.project)}</td>
      <td class="td-mono">${esc(b.branch)}${b.protected ? ' <span class="tag-protected">protected</span>' : ''}</td>
      <td>${sha} <span class="commit-title" title="${esc(b.commit_title)}">${esc(b.commit_title)}</span></td>
      <td>${esc(b.commit_author)}</td>
      <td>${pipelineBadge}</td>
      <td>${fmtDateShort(b.committed_at)}</td>
    </tr>`;
  }).join('');
}

function renderMrsTable(tbodyId, rows) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  if (!rows.length) { tbody.innerHTML = '<tr class="loading-row"><td colspan="5">No merge requests found</td></tr>'; return; }
  tbody.innerHTML = rows.map(m => `
    <tr>
      <td class="td-main">${esc(m.project)}</td>
      <td><a href="${esc(m.web_url)}" target="_blank">${esc(m.title)}</a></td>
      <td>${esc(m.author)}</td>
      <td>${badge(m.state)}</td>
      <td>${fmtDateShort(m.updated_at)}</td>
    </tr>`).join('');
}

function renderDeploymentsTable(tbodyId, rows) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  if (!rows.length) { tbody.innerHTML = '<tr class="loading-row"><td colspan="6">No deployments found</td></tr>'; return; }
  tbody.innerHTML = rows.map(d => `
    <tr>
      <td class="td-main">${esc(d.project)}</td>
      <td class="td-mono">${esc(d.environment)}</td>
      <td class="td-mono">${esc(d.ref)}</td>
      <td>${badge(d.status)}</td>
      <td>${userCell(d.deployed_by, d.deployed_by_avatar)}</td>
      <td>${fmtDateShort(d.updated_at)}</td>
    </tr>`).join('');
}

// ── Overview ─────────────────────────────────────────────────────────────────
function updateOverviewCards(d) {
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set('ov-total', d.total_pipelines ?? '-');
  set('ov-total-sub', `${d.success ?? 0} success / ${d.failed ?? 0} failed`);
  set('ov-rate', d.success_rate != null ? d.success_rate + '%' : '-');
  set('ov-rate-sub', `${d.success ?? 0} successful pipelines`);
  set('ov-failed', d.failed ?? '-');
  set('ov-failed-sub', `${d.canceled ?? 0} canceled`);
  set('ov-running', d.running ?? '-');
  set('ov-running-sub', `${d.pending ?? 0} pending`);
  set('ov-dur', d.avg_duration_s != null ? fmtDur(d.avg_duration_s) : '-');
  set('ov-mrs', d.open_mrs ?? '-');
  set('ov-mrs-sub', 'awaiting review');
  set('ov-projects', d.total_projects ?? '-');
}

async function loadOverview() {
  const days = State.dateFilter;

  try {
    const d = await apiFetch(`/api/overview?days=${days}`);
    updateOverviewCards(d);
  } catch (e) { showToast('Failed to load overview: ' + e.message, 'error'); }

  try {
    const trendDays = Math.min(days, 30); // Cap trend chart at 30 days for readability
    const trend = await apiFetch(`/api/pipelines/trend?days=${trendDays}`);
    const trendLabel = document.getElementById('chart-trend-label');
    if (trendLabel) trendLabel.textContent = `(${trendDays} days)`;

    buildLineChart('chart-trend',
      trend.map(r => r.date.slice(5)),
      [
        makeDataset('Total',   trend.map(r => r.total),   PALETTE[0], { fill: true }),
        makeDataset('Success', trend.map(r => r.success), PALETTE[1], {}),
        makeDataset('Failed',  trend.map(r => r.failed),  PALETTE[2], {}),
      ]
    );
  } catch (_) {}

  try {
    const status = await apiFetch(`/api/pipelines/status?days=${days}`);
    const labels = ['Success','Failed','Running','Pending','Canceled','Skipped'];
    const vals   = [status.success, status.failed, status.running, status.pending, status.canceled, status.skipped];
    const colors = ['#10b981','#ef4444','#3b82f6','#f59e0b','#5d6785','#5d6785'];
    buildDoughnutChart('chart-status', labels, vals, colors);
  } catch (_) {}

  try {
    const branches = await apiFetch('/api/branches/overview');
    renderBranchTable('table-ov-branches', branches);
  } catch (e) {
    const tbody = document.getElementById('table-ov-branches');
    if (tbody) tbody.innerHTML = `<tr class="loading-row"><td colspan="6">Error: ${esc(e.message)}</td></tr>`;
  }

  try {
    const mrs = await apiFetch('/api/mrs/recent?limit=15');
    renderMrsTable('table-ov-mrs', mrs);
  } catch (e) {
    const tbody = document.getElementById('table-ov-mrs');
    if (tbody) tbody.innerHTML = `<tr class="loading-row"><td colspan="5">Error: ${esc(e.message)}</td></tr>`;
  }

  try {
    const deps = await apiFetch('/api/deployments/recent?limit=15');
    renderDeploymentsTable('table-ov-deployments', deps);
  } catch (e) {
    const tbody = document.getElementById('table-ov-deployments');
    if (tbody) tbody.innerHTML = `<tr class="loading-row"><td colspan="6">Error: ${esc(e.message)}</td></tr>`;
  }

  try {
    const mrTrend = await apiFetch(`/api/mrs/trend?days=${days}`);
    const canvas = document.getElementById('chart-mr-trend');
    const emptyMsg = document.getElementById('chart-mr-trend-empty');

    if (mrTrend && mrTrend.length > 0) {
      const hasData = mrTrend.some(r => (r.opened || 0) + (r.merged || 0) + (r.closed || 0) > 0);

      if (hasData) {
        if (canvas) canvas.style.display = 'block';
        if (emptyMsg) emptyMsg.style.display = 'none';
        buildLineChart('chart-mr-trend',
          mrTrend.map(r => r.date.slice(5)),
          [
            makeDataset('Opened', mrTrend.map(r => r.opened || 0), PALETTE[0], { fill: true }),
            makeDataset('Merged', mrTrend.map(r => r.merged || 0), PALETTE[1], {}),
            makeDataset('Closed', mrTrend.map(r => r.closed || 0), PALETTE[2], {}),
          ]
        );
      } else {
        if (canvas) canvas.style.display = 'none';
        if (emptyMsg) emptyMsg.style.display = 'block';
      }
    } else {
      if (canvas) canvas.style.display = 'none';
      if (emptyMsg) emptyMsg.style.display = 'block';
    }
  } catch (e) {
    console.error('Failed to load MR trend chart:', e);
    const canvas = document.getElementById('chart-mr-trend');
    const emptyMsg = document.getElementById('chart-mr-trend-empty');
    if (canvas) canvas.style.display = 'none';
    if (emptyMsg) {
      emptyMsg.textContent = 'Error loading merge request data: ' + e.message;
      emptyMsg.style.display = 'block';
    }
  }
}

// ── Pipelines ─────────────────────────────────────────────────────────────────
async function loadPipelines() {
  try {
    const rows = await apiFetch('/api/pipelines/recent?limit=30');
    const tbody = document.getElementById('table-pipelines');
    if (!tbody) return;
    if (!rows.length) { tbody.innerHTML = '<tr class="loading-row"><td colspan="8">No pipelines found</td></tr>'; return; }
    tbody.innerHTML = rows.map(p => `
      <tr>
        <td class="td-main">${esc(p.project)}</td>
        <td><a href="${esc(p.web_url)}" target="_blank">#${esc(p.id)}</a></td>
        <td class="td-mono">${esc(p.ref)}</td>
        <td>${badge(p.status)}</td>
        <td>${fmtDur(p.duration)}</td>
        <td>${fmtDateShort(p.created_at)}</td>
        <td class="td-mono">${esc(p.sha)}</td>
        <td>${userCell(p.triggered_by, p.triggered_by_avatar)}</td>
      </tr>`).join('');
  } catch (e) {
    const tbody = document.getElementById('table-pipelines');
    if (tbody) tbody.innerHTML = `<tr class="loading-row"><td colspan="8">Error: ${esc(e.message)}</td></tr>`;
  }
}

// ── Jobs ──────────────────────────────────────────────────────────────────────
async function loadJobs() {
  try {
    const failing = await apiFetch('/api/jobs/top-failing?limit=10');
    if (failing.length) {
      buildBarChart('chart-failing',
        failing.map(j => j.name.length > 22 ? j.name.slice(0,22) + '...' : j.name),
        [{ label: 'Failures', data: failing.map(j => j.failures), backgroundColor: hexToRgba('#ef4444', 0.75) }],
        { horizontal: true }
      );
    }
  } catch (_) {}

  try {
    const stages = await apiFetch('/api/jobs/stages');
    if (stages.length) {
      buildBarChart('chart-stages',
        stages.map(s => s.stage),
        [
          { label: 'Success', data: stages.map(s => s.success), backgroundColor: hexToRgba('#10b981', 0.75) },
          { label: 'Failed',  data: stages.map(s => s.failed),  backgroundColor: hexToRgba('#ef4444', 0.75) },
        ]
      );
    }
  } catch (_) {}

  try {
    const rows = await apiFetch('/api/jobs/recent?limit=30');
    const tbody = document.getElementById('table-jobs');
    if (!tbody) return;
    if (!rows.length) { tbody.innerHTML = '<tr class="loading-row"><td colspan="7">No jobs found</td></tr>'; return; }
    tbody.innerHTML = rows.map(j => `
      <tr>
        <td class="td-main">${esc(j.project)}</td>
        <td><a href="${esc(j.web_url)}" target="_blank">${esc(j.name)}</a></td>
        <td class="td-mono">${esc(j.stage)}</td>
        <td>${badge(j.status)}</td>
        <td>${fmtDur(j.duration)}</td>
        <td class="td-mono">${esc(j.ref)}</td>
        <td>${fmtDateShort(j.created_at)}</td>
      </tr>`).join('');
  } catch (e) {
    const tbody = document.getElementById('table-jobs');
    if (tbody) tbody.innerHTML = `<tr class="loading-row"><td colspan="7">Error: ${esc(e.message)}</td></tr>`;
  }
}

// ── Navigation ────────────────────────────────────────────────────────────────
const SECTION_LOADERS = {
  overview:       loadOverview,
  pipelines:      loadPipelines,
  jobs:           loadJobs,
};

function switchSection(name) {
  State.section = name;
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.section === name));
  document.querySelectorAll('.section').forEach(s => s.classList.toggle('active', s.id === 'section-' + name));
  if (SECTION_LOADERS[name]) SECTION_LOADERS[name]();
}

// ── API fetch ─────────────────────────────────────────────────────────────────
async function apiFetch(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

// ── Export ────────────────────────────────────────────────────────────────────
function doExport(fmt) {
  document.getElementById('export-menu').classList.remove('open');
  showToast('Preparing ' + fmt.toUpperCase() + ' export...', '');
  fetch('/api/export/' + fmt)
    .then(r => {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.blob();
    })
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'cicd_export.' + fmt;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Export downloaded', 'success');
    })
    .catch(e => showToast('Export failed: ' + e.message, 'error'));
}

// ── Auto-refresh ──────────────────────────────────────────────────────────────
function startRefresh() {
  clearInterval(State.refreshTimer);
  State.refreshTimer = setInterval(() => {
    if (SECTION_LOADERS[State.section]) SECTION_LOADERS[State.section]();
  }, State.REFRESH_MS);
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  applyTheme();
  connectWS();

  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => switchSection(btn.dataset.section));
  });

  document.getElementById('theme-btn').addEventListener('click', toggleTheme);

  const exportBtn = document.getElementById('export-btn');
  const exportMenu = document.getElementById('export-menu');
  exportBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    exportMenu.classList.toggle('open');
  });
  document.addEventListener('click', () => exportMenu.classList.remove('open'));

  // Date filter menu
  const filterBtn = document.getElementById('filter-btn');
  const filterMenu = document.getElementById('filter-menu');
  filterBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    filterMenu.classList.toggle('open');
  });

  // Date filter options
  document.querySelectorAll('#filter-menu a').forEach(a => {
    a.addEventListener('click', (e) => {
      e.stopPropagation();
      const days = parseInt(a.dataset.days);
      setDateFilter(days);
      filterMenu.classList.remove('open');
    });
  });

  // Close filter menu when clicking outside
  document.addEventListener('click', () => filterMenu.classList.remove('open'));

  // Initialize date filter on load
  setDateFilter(State.dateFilter);

  loadOverview();
  startRefresh();
});
