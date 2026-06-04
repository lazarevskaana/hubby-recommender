const API = 'http://localhost:8000';
const FALLBACK = { lat: 42.0, lon: 21.43 };
const MAX_LIMIT = 200;

const el = (id) => document.getElementById(id);
const fUser   = el('f-user');
const fLat    = el('f-lat');
const fLon    = el('f-lon');
const fCtx    = el('f-ctx');
const fRadius = el('f-radius');
const fGo     = el('f-go');
const resultsEl = el('results');
const metaEl    = el('meta');
const stateEl   = el('state');
const popoverEl = el('detail-popover');
const userSuggestEl = el('user-suggestions');

let map, userMarker = null, actMarkers = [];
let lastResults = [];
let allUsers = [];

// ── Helpers ─────────────────────────────────────────────────────────
function humanize(s) {
  if (!s) return '';
  return s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function fmtDist(km) {
  if (km == null) return '';
  return km < 1 ? `${Math.round(km * 1000)}m away` : `${km.toFixed(2)}km away`;
}

function stars(rating) {
  const r = Math.round(rating || 0);
  return '★★★★★☆☆☆☆☆'.slice(5 - r, 10 - r);
}

function subtypeEmoji(t) {
  const m = {
    restaurant: '🍽️', cafe: '☕', bar: '🍸', bakery: '🥐', night_club: '🎶',
    pub: '🍺', museum: '🏛️', park: '🌳', attraction: '📸', food: '🍽️',
    movie_theater: '🎬', hotel: '🏨', other: '📍',
    vegetarian_restaurant: '🥗', vegan_restaurant: '🌱', sushi_restaurant: '🍣',
    hamburger_restaurant: '🍔', mexican_restaurant: '🌮', barbecue_restaurant: '🍖',
    bistro: '🍷', pizza_restaurant: '🍕', italian_restaurant: '🍝',
    fast_food_restaurant: '🍟', coffee_shop: '☕', cake_shop: '🍰',
    art_gallery: '🎨', tourist_attraction: '🗺️',
  };
  return m[t] || '📍';
}

function googleMapsUrl(r) {
  const name = (r.name || '').trim();
  if (r.latitude && r.longitude && name) {
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(name + ' ' + r.latitude + ' ' + r.longitude)}`;
  }
  if (name) return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(name)}`;
  return `https://www.google.com/maps/search/?api=1&query=${r.latitude},${r.longitude}`;
}

// ── Today's working hours ────────────────────────────────────────────
// working_hours is an object like:
// { monday: [{open:"09:00", close:"23:00"}], tuesday: [...], ... }
// Some days may be null (no data), [] (closed), or missing.
const DAY_NAMES = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday'];

function getTodayHours(workingHours) {
  if (!workingHours || typeof workingHours !== 'object') return null;
  const today = DAY_NAMES[new Date().getDay()];
  const slots = workingHours[today];

  // null = no data available
  if (slots === null || slots === undefined) return null;

  // empty array = closed today
  if (Array.isArray(slots) && slots.length === 0) return { label: 'Closed today', closed: true };

  if (Array.isArray(slots) && slots.length > 0) {
    const times = slots.map(s => `${s.open}–${s.close}`).join(', ');
    return { label: times, closed: false };
  }
  return null;
}

// ── User name autocomplete ───────────────────────────────────────────
async function loadAllUsers() {
  try {
    const res = await fetch(`${API}/users?limit=100`);
    if (!res.ok) return;
    allUsers = await res.json();
  } catch(e) { /* silently fail */ }
}

function showUserSuggestions(query) {
  if (!query || query.length < 2) {
    userSuggestEl.innerHTML = '';
    userSuggestEl.classList.add('hidden');
    return;
  }
  const q = query.toLowerCase();
  const matches = allUsers.filter(u =>
    `${u.name} ${u.surname}`.toLowerCase().includes(q)
  ).slice(0, 8);

  if (matches.length === 0) {
    userSuggestEl.innerHTML = '';
    userSuggestEl.classList.add('hidden');
    return;
  }

  userSuggestEl.innerHTML = matches.map(u => `
    <div class="suggest-item" data-id="${u.id}" data-lat="${u.latitude}" data-lon="${u.longitude}">
      <span class="font-semibold">${u.name} ${u.surname}</span>
      <span class="text-xs text-hubby-ink/50 ml-2">#${u.id}</span>
    </div>
  `).join('');
  userSuggestEl.classList.remove('hidden');

  userSuggestEl.querySelectorAll('.suggest-item').forEach(item => {
    item.addEventListener('click', () => {
      fUser.value = item.querySelector('.font-semibold').textContent;
      fUser.dataset.selectedId = item.dataset.id;
      fLat.value = parseFloat(item.dataset.lat).toFixed(6);
      fLon.value = parseFloat(item.dataset.lon).toFixed(6);
      fLat.disabled = true;
      fLon.disabled = true;
      userSuggestEl.classList.add('hidden');
      search();
    });
  });
}

// ── Map init ──────────────────────────────────────────────────────────
map = L.map('map', { zoomControl: true }).setView([FALLBACK.lat, FALLBACK.lon], 14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap', maxZoom: 19,
}).addTo(map);

function pinIcon(kind, emoji) {
  return L.divIcon({
    className: '',
    html: `<div class="marker-pin marker-${kind}">${emoji}</div>`,
    iconSize: [30, 30], iconAnchor: [15, 15],
  });
}

function clearMarkers() {
  actMarkers.forEach(m => map.removeLayer(m));
  actMarkers = [];
}

function setUserMarker(lat, lon) {
  if (userMarker) map.removeLayer(userMarker);
  userMarker = L.marker([lat, lon], { icon: pinIcon('user', '📍') })
    .addTo(map)
    .bindPopup(`<div style="padding:14px 16px;"><div style="font-weight:700;color:#FF8800;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">Your location</div><div style="font-weight:600;color:#2D3748;font-size:14px;">You are here</div></div>`);
}

function buildMapPopup(r) {
  const emoji = subtypeEmoji(r.subtype || r.type);
  const subLabel = humanize(r.subtype || r.type);
  const pct = Math.round((r.scores?.final || 0) * 100);
  const todayHrs = getTodayHours(r.working_hours);
  const hoursHtml = todayHrs
    ? `<div style="font-size:11px;color:${todayHrs.closed ? '#EF4444' : '#6B7280'};margin-bottom:8px;">🕐 ${todayHrs.label}</div>`
    : '';

  return `
    <div style="padding:0;">
      <div style="background:linear-gradient(135deg,#FF8800 0%,#FFB347 100%);padding:10px 14px;color:white;">
        <div style="font-size:11px;opacity:0.9;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;">${emoji} ${subLabel}</div>
      </div>
      <div style="padding:12px 14px;">
        <div style="font-family:'Outfit',sans-serif;font-weight:700;font-size:16px;color:#2D3748;margin-bottom:6px;line-height:1.2;">${r.name}</div>
        <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#6B7280;margin-bottom:8px;">
          <span style="color:#FFB347;">${stars(r.rating)}</span>
          <span style="font-weight:600;color:#2D3748;">${(r.rating ?? 0).toFixed(1)}</span>
          <span>· ${r.user_rating_count ?? 0} reviews</span>
        </div>
        ${hoursHtml}
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
          <span style="font-size:11px;font-weight:600;padding:4px 10px;border-radius:999px;background:#FFF5EC;color:#FF8800;">${fmtDist(r.distance_km)}</span>
          <span style="font-size:13px;font-weight:700;color:#FF8800;">Score: ${pct}</span>
        </div>
      </div>
    </div>`;
}

// ── Card HTML ─────────────────────────────────────────────────────────
function cardHTML(r, idx) {
  const emoji = subtypeEmoji(r.subtype || r.type);
  const subLabel = humanize(r.subtype || r.type || 'place');
  const pct = Math.round((r.scores?.final ?? 0) * 100);
  const todayHrs = getTodayHours(r.working_hours);
  const scoreBreak = r.scores ? [
    ['Distance',   r.scores.distance],
    ['Category',   r.scores.category_relevance],
    ['Rating',     r.scores.rating],
    ['Popularity', r.scores.popularity],
  ] : [];

  const hoursHtml = todayHrs
    ? `<div class="mt-1 flex items-center gap-1 text-xs font-medium ${todayHrs.closed ? 'text-red-500' : 'text-hubby-ink/60'}">
         <span>🕐</span><span>${todayHrs.label}</span>
       </div>`
    : '';

  return `
  <article class="rec-card bg-white rounded-3xl overflow-hidden shadow-card" data-idx="${idx}">
    <div class="relative h-14 bg-gradient-to-br from-orange-50 to-orange-100 flex items-center px-4">
      <div class="bg-white/95 backdrop-blur px-3 py-1.5 rounded-full text-xs font-semibold text-hubby-ink shadow">
        ${emoji} ${subLabel}
      </div>
      ${r.is_open === false ? '<div class="ml-auto bg-red-500/90 text-white px-3 py-1.5 rounded-full text-xs font-semibold">Closed</div>' : ''}
    </div>
    <div class="p-5">
      <div class="flex items-start justify-between gap-3">
        <h3 class="font-display font-bold text-xl text-hubby-ink leading-tight">${r.name}</h3>
        <span class="shrink-0 text-xs font-semibold px-3 py-1.5 rounded-full bg-orange-100 text-hubby-orange">${fmtDist(r.distance_km)}</span>
      </div>
      <div class="mt-2 flex items-center gap-2 text-sm text-hubby-ink/70">
        <span class="text-hubby-yellow text-base tracking-tight">${stars(r.rating)}</span>
        <span class="font-semibold text-hubby-ink">${(r.rating ?? 0).toFixed(1)}</span>
        <span class="text-hubby-ink/40">·</span>
        <span>${r.user_rating_count ?? 0} reviews</span>
      </div>
      ${hoursHtml}
      <div class="mt-4">
        <div class="flex items-center justify-between mb-1.5">
          <span class="text-xs uppercase tracking-wider text-hubby-ink/50 font-semibold">Final score</span>
          <span class="font-display font-bold text-2xl text-hubby-orange">${pct}</span>
        </div>
        <div class="w-full bg-orange-50 rounded-full h-2">
          <div class="score-bar" style="width:${pct}%"></div>
        </div>
      </div>
      <div class="mt-4 grid grid-cols-4 gap-2">
        ${scoreBreak.map(([k, v]) => `
          <div class="text-center">
            <div class="text-[10px] uppercase tracking-wider text-hubby-ink/50 font-semibold">${k}</div>
            <div class="mt-1 h-1.5 bg-orange-50 rounded-full overflow-hidden">
              <div style="width:${Math.round((v || 0) * 100)}%" class="h-full bg-hubby-coral"></div>
            </div>
            <div class="text-[11px] font-semibold text-hubby-ink/70 mt-1">${Math.round((v || 0) * 100)}</div>
          </div>
        `).join('')}
      </div>
    </div>
  </article>`;
}

// ── Popover HTML ──────────────────────────────────────────────────────
function popoverHTML(r) {
  const emoji = subtypeEmoji(r.subtype || r.type);
  const subLabel = humanize(r.subtype || r.type || 'place');
  const typeLabel = humanize(r.type || '');
  const pct = Math.round((r.scores?.final ?? 0) * 100);
  const mapsLink = googleMapsUrl(r);
  const todayHrs = getTodayHours(r.working_hours);
  const hoursHtml = todayHrs
    ? `<div class="flex items-center gap-2 text-sm font-medium ${todayHrs.closed ? 'text-red-500' : 'text-hubby-ink/60'}">
         <span>🕐</span><span>${todayHrs.label}</span>
       </div>`
    : '';

  return `
    <div class="bg-gradient-to-br from-hubby-orange to-hubby-yellow text-white px-6 py-5">
      <div class="text-xs font-bold uppercase tracking-wider opacity-90 mb-1">${emoji} ${subLabel}</div>
      <div class="font-display font-extrabold text-2xl leading-tight">${r.name}</div>
      ${typeLabel && typeLabel.toLowerCase() !== subLabel.toLowerCase() ? `<div class="text-xs opacity-80 mt-1">Category: ${typeLabel}</div>` : ''}
    </div>
    <div class="px-6 py-5 space-y-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-hubby-yellow text-lg">${stars(r.rating)}</span>
          <span class="font-bold text-hubby-ink">${(r.rating ?? 0).toFixed(1)}</span>
          <span class="text-hubby-ink/60 text-sm">(${r.user_rating_count ?? 0} reviews)</span>
        </div>
        <span class="text-xs font-semibold px-3 py-1.5 rounded-full bg-orange-100 text-hubby-orange">${fmtDist(r.distance_km)}</span>
      </div>
      ${hoursHtml}
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs uppercase tracking-wider text-hubby-ink/50 font-bold">Recommendation score</span>
          <span class="font-display font-extrabold text-3xl text-hubby-orange">${pct}</span>
        </div>
        <div class="w-full bg-orange-50 rounded-full h-2.5">
          <div class="score-bar" style="width:${pct}%"></div>
        </div>
      </div>
      <div>
        <div class="text-xs uppercase tracking-wider text-hubby-ink/50 font-bold mb-2">Why this ranking</div>
        <div class="space-y-2">
          ${[['Distance', r.scores?.distance],['Category', r.scores?.category_relevance],['Rating', r.scores?.rating],['Popularity', r.scores?.popularity]]
            .map(([k, v]) => `
              <div>
                <div class="flex items-center justify-between text-xs mb-0.5">
                  <span class="font-semibold text-hubby-ink">${k}</span>
                  <span class="text-hubby-ink/60">${Math.round((v || 0) * 100)}</span>
                </div>
                <div class="h-1.5 bg-orange-50 rounded-full overflow-hidden">
                  <div style="width:${Math.round((v || 0) * 100)}%" class="h-full bg-hubby-coral"></div>
                </div>
              </div>`).join('')}
        </div>
      </div>
      <div class="text-xs text-hubby-ink/50 pt-1 border-t border-orange-100">
        📍 ${r.latitude?.toFixed(5)}, ${r.longitude?.toFixed(5)}
      </div>
      <a href="${mapsLink}" target="_blank" rel="noopener noreferrer"
         class="block w-full bg-hubby-ink hover:bg-black text-white text-center font-semibold rounded-2xl py-3 transition flex items-center justify-center gap-2">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
        Open in Google Maps
      </a>
    </div>`;
}

// ── Popover positioning ───────────────────────────────────────────────
function positionPopover(cardEl) {
  const rect = cardEl.getBoundingClientRect();
  const pw = 380, margin = 12;
  let left = rect.right + margin;
  let top = rect.top;
  if (left + pw > window.innerWidth - 8) left = rect.left - pw - margin;
  if (left < 8) { left = Math.max(8, (window.innerWidth - pw) / 2); top = rect.bottom + margin; }
  const h = popoverEl.scrollHeight || 500;
  if (top + h > window.innerHeight - 8) top = Math.max(8, window.innerHeight - h - 8);
  popoverEl.style.left = left + 'px';
  popoverEl.style.top = top + 'px';
  popoverEl.style.maxHeight = (window.innerHeight - 40) + 'px';
  popoverEl.style.overflowY = 'auto';
}

let popoverHideTimer = null;
function showPopover(cardEl, item) {
  clearTimeout(popoverHideTimer);
  popoverEl.innerHTML = popoverHTML(item);
  popoverEl.classList.add('visible');
  requestAnimationFrame(() => positionPopover(cardEl));
}
function hidePopover() {
  popoverHideTimer = setTimeout(() => popoverEl.classList.remove('visible'), 120);
}
popoverEl.addEventListener('mouseenter', () => clearTimeout(popoverHideTimer));
popoverEl.addEventListener('mouseleave', hidePopover);

function attachCardHovers() {
  document.querySelectorAll('.rec-card').forEach(card => {
    const idx = parseInt(card.dataset.idx, 10);
    card.addEventListener('mouseenter', () => { const item = lastResults[idx]; if (item) showPopover(card, item); });
    card.addEventListener('mouseleave', hidePopover);
  });
}

// ── Render results ────────────────────────────────────────────────────
function renderResults(data) {
  const items = data.results || [];
  lastResults = items;

  if (items.length === 0) {
    stateEl.innerHTML = `<div class="bg-orange-50/60 border border-orange-100 rounded-3xl p-8 text-center">
      <div class="text-4xl mb-2">🌴</div>
      <div class="font-display font-bold text-xl text-hubby-ink">No places open right now</div>
      <div class="text-hubby-ink/60 mt-1">Try a wider radius or a different context.</div>
    </div>`;
    metaEl.innerHTML = '';
    resultsEl.innerHTML = '';
    clearMarkers();
    return;
  }

  resultsEl.innerHTML = '';
  clearMarkers();

  const lat = data.user_latitude ?? parseFloat(fLat.value);
  const lon = data.user_longitude ?? parseFloat(fLon.value);
  if (!isNaN(lat) && !isNaN(lon)) {
    setUserMarker(lat, lon);
    map.setView([lat, lon], 14);
    setTimeout(() => map.invalidateSize(), 50);
  }

  metaEl.innerHTML = `
    <div>Showing <span class="font-bold text-hubby-ink">${items.length}</span> recommendations
      <span class="text-hubby-ink/40">·</span>
      context: <span class="font-semibold text-hubby-orange">${data.context}</span>
    </div>
    <div class="text-xs text-hubby-ink/50">radius ${data.radius_km}km</div>`;

  resultsEl.insertAdjacentHTML('beforeend', items.map((r, idx) => cardHTML(r, idx)).join(''));
  attachCardHovers();

  items.forEach(r => {
    if (r.latitude && r.longitude) {
      const m = L.marker([r.latitude, r.longitude], { icon: pinIcon('act', subtypeEmoji(r.subtype || r.type)) })
        .bindPopup(buildMapPopup(r), { maxWidth: 260, className: 'hubby-popup' })
        .addTo(map);
      actMarkers.push(m);
    }
  });
  stateEl.innerHTML = '';
}

// ── Fetch user by ID ──────────────────────────────────────────────────
async function fetchUserCoords(userId) {
  const res = await fetch(`${API}/users/${encodeURIComponent(userId)}`);
  if (!res.ok) throw new Error(res.status === 404 ? 'User not found' : `HTTP ${res.status}`);
  return await res.json();
}

// ── Main search ───────────────────────────────────────────────────────
async function search() {
  stateEl.innerHTML = `<div class="flex flex-col items-center gap-3 py-10"><div class="spinner"></div><div class="text-hubby-ink/70 font-medium">Loading recommendations…</div></div>`;
  resultsEl.innerHTML = '';
  clearMarkers();
  popoverEl.classList.remove('visible');

  const selectedUserId = fUser.dataset.selectedId;
  const radius = fRadius.value || '1.0';
  const ctx = fCtx.value;

  if (selectedUserId) {
    try {
      const userData = await fetchUserCoords(selectedUserId);
      if (userData.latitude != null) { fLat.value = userData.latitude.toFixed(6); fLon.value = userData.longitude.toFixed(6); }
    } catch (e) {
      stateEl.innerHTML = `<div class="bg-red-50 border border-red-200 rounded-3xl p-6 text-center"><div class="text-2xl mb-1">⚠️</div><div class="font-semibold text-red-700">${e.message}</div></div>`;
      return;
    }
  }

  const params = new URLSearchParams({ radius_km: radius, limit: MAX_LIMIT });
  if (ctx) params.set('context', ctx);

  let url;
  if (selectedUserId) {
    url = `${API}/recommendations/${encodeURIComponent(selectedUserId)}?${params}`;
  } else {
    params.set('lat', fLat.value);
    params.set('lon', fLon.value);
    url = `${API}/recommendations?${params}`;
  }

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    renderResults(await res.json());
  } catch (e) {
    console.error(e);
    stateEl.innerHTML = `<div class="bg-red-50 border border-red-200 rounded-3xl p-6 text-center"><div class="text-2xl mb-1">⚠️</div><div class="font-semibold text-red-700">Could not reach the API (${e.message}). Is uvicorn running at ${API}?</div></div>`;
  }
}

// ── Event listeners ───────────────────────────────────────────────────
fGo.addEventListener('click', search);
[fLat, fLon, fRadius].forEach(i => i.addEventListener('keydown', e => { if (e.key === 'Enter') search(); }));
fCtx.addEventListener('change', search);

fUser.addEventListener('input', () => {
  delete fUser.dataset.selectedId;
  fLat.disabled = false;
  fLon.disabled = false;
  showUserSuggestions(fUser.value.trim());
});
fUser.addEventListener('keydown', e => {
  if (e.key === 'Enter') { userSuggestEl.classList.add('hidden'); search(); }
  if (e.key === 'Escape') userSuggestEl.classList.add('hidden');
});
document.addEventListener('click', e => {
  if (!fUser.contains(e.target) && !userSuggestEl.contains(e.target)) userSuggestEl.classList.add('hidden');
});
window.addEventListener('scroll', () => popoverEl.classList.remove('visible'), { passive: true });

// ── Bootstrap ─────────────────────────────────────────────────────────
function bootstrap(lat, lon) {
  fLat.value = lat.toFixed(6);
  fLon.value = lon.toFixed(6);
  setUserMarker(lat, lon);
  map.setView([lat, lon], 14);
  search();
}

loadAllUsers().then(() => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      p => bootstrap(p.coords.latitude, p.coords.longitude),
      _ => bootstrap(FALLBACK.lat, FALLBACK.lon),
      { timeout: 5000 }
    );
  } else {
    bootstrap(FALLBACK.lat, FALLBACK.lon);
  }
});