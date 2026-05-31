const API = 'http://localhost:8000';
const FALLBACK = { lat: 42.0, lon: 21.43 };
const MAX_LIMIT = 200;  // match backend MAX_LIMIT

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

let map, userMarker = null, actMarkers = [];

// ── Map init ─────────────────────────────────────────────────────────
map = L.map('map', { zoomControl: true }).setView([FALLBACK.lat, FALLBACK.lon], 14);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap',
  maxZoom: 19,
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
    .addTo(map).bindPopup('<b>You are here</b>');
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
    movie_theater: '🎬', hotel: '🏨', other: '📍'
  };
  return m[t] || '📍';
}

function cardHTML(r) {
  const emoji = subtypeEmoji(r.subtype || r.type);
  const sub   = (r.subtype || r.type || 'place');
  const pct   = Math.round((r.scores?.final ?? 0) * 100);
  const scoreBreak = r.scores ? [
    ['Distance',   r.scores.distance],
    ['Category',   r.scores.category_relevance],
    ['Rating',     r.scores.rating],
    ['Popularity', r.scores.popularity],
  ] : [];

  return `
  <article class="rec-card bg-white rounded-3xl overflow-hidden shadow-card">
    <div class="relative h-14 bg-gradient-to-br from-orange-50 to-orange-100 flex items-center px-4">
      <div class="bg-white/95 backdrop-blur px-3 py-1.5 rounded-full text-xs font-semibold text-hubby-ink shadow">
        ${emoji} ${sub.charAt(0).toUpperCase() + sub.slice(1)}
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

function renderResults(data) {
  const items = data.results || [];
  if (items.length === 0) {
    stateEl.innerHTML = `<div class="bg-orange-50/60 border border-orange-100 rounded-3xl p-8 text-center">
      <div class="text-4xl mb-2">🌴</div>
      <div class="font-display font-bold text-xl text-hubby-ink">No places open right now</div>
      <div class="text-hubby-ink/60 mt-1">Try a wider radius or a different context.</div>
    </div>`;
    metaEl.innerHTML = '';
    return;
  }

  // Clear previous results
  resultsEl.innerHTML = '';
  clearMarkers();

  // Update map and center
  const lat = data.user_latitude ?? parseFloat(fLat.value);
  const lon = data.user_longitude ?? parseFloat(fLon.value);
  if (!isNaN(lat) && !isNaN(lon)) {
    setUserMarker(lat, lon);
    map.setView([lat, lon], 14);
  }

  // Update meta info
  metaEl.innerHTML = `
    <div>Showing <span class="font-bold text-hubby-ink">${items.length}</span> recommendations
      <span class="text-hubby-ink/40">·</span>
      context: <span class="font-semibold text-hubby-orange">${data.context || 'auto'}</span>
    </div>
    <div class="text-xs text-hubby-ink/50">radius ${data.radius_km}km</div>
  `;

  // Render cards and markers
  resultsEl.insertAdjacentHTML('beforeend', items.map(cardHTML).join(''));
  items.forEach(r => {
    if (r.latitude && r.longitude) {
      const m = L.marker([r.latitude, r.longitude], { icon: pinIcon('act', subtypeEmoji(r.subtype || r.type)) })
        .bindPopup(`<b>${r.name}</b><br/>${r.subtype || r.type || ''}<br/>${fmtDist(r.distance_km)}<br/>Score: <b>${Math.round((r.scores?.final || 0) * 100)}</b>`)
        .addTo(map);
      actMarkers.push(m);
    }
  });
  stateEl.innerHTML = ''; // clear any loading/error
}

async function search() {
  stateEl.innerHTML = `<div class="flex flex-col items-center gap-3 py-10"><div class="spinner"></div><div class="text-hubby-ink/70 font-medium">Loading recommendations…</div></div>`;
  resultsEl.innerHTML = '';
  clearMarkers();

  const user = fUser.value.trim();
  const radius = fRadius.value || '1.0';
  const ctx = fCtx.value;
  const params = new URLSearchParams();
  params.set('radius_km', radius);
  params.set('limit', MAX_LIMIT);
  if (ctx) params.set('context', ctx);

  let url;
  if (user) {
    url = `${API}/recommendations/${encodeURIComponent(user)}?${params.toString()}`;
  } else {
    params.set('lat', fLat.value);
    params.set('lon', fLon.value);
    url = `${API}/recommendations?${params.toString()}`;
  }

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderResults(data);
  } catch (e) {
    console.error(e);
    stateEl.innerHTML = `<div class="bg-red-50 border border-red-200 rounded-3xl p-6 text-center">
      <div class="text-2xl mb-1">⚠️</div>
      <div class="font-semibold text-red-700">Could not reach the API (${e.message}). Is uvicorn running at ${API}?</div>
    </div>`;
  }
}

// ── Event listeners ───────────────────────────────────────────────────
fGo.addEventListener('click', search);
[fUser, fLat, fLon, fRadius].forEach(i =>
  i.addEventListener('keydown', e => { if (e.key === 'Enter') search(); })
);
fCtx.addEventListener('change', search);
fUser.addEventListener('input', () => {
  const hasUser = fUser.value.trim().length > 0;
  fLat.disabled = hasUser;
  fLon.disabled = hasUser;
});

// ── Geolocation bootstrap ─────────────────────────────────────────────
function bootstrap(lat, lon) {
  fLat.value = lat.toFixed(6);
  fLon.value = lon.toFixed(6);
  setUserMarker(lat, lon);
  map.setView([lat, lon], 14);
  search();
}

if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(
    p  => bootstrap(p.coords.latitude, p.coords.longitude),
    _  => bootstrap(FALLBACK.lat, FALLBACK.lon),
    { timeout: 5000 }
  );
} else {
  bootstrap(FALLBACK.lat, FALLBACK.lon);
}