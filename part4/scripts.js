cat > /root/holbertonschool-hbnb/part4/scripts.js <<'JS'
/* --- tiny auth helpers --- */
function getCookie(name){
  return document.cookie.split("; ").reduce((acc,cur)=>{
    const [k,v]=cur.split("="); return k===name?decodeURIComponent(v):acc;
  }, "");
}
async function apiFetch(path, options={}){
  const token = getCookie("token");
  const headers = { "Content-Type":"application/json", ...(options.headers||{}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(path, { ...options, headers });
  if (res.status === 401) {
    // not logged in or token expired
    location.href = "login.html";
    throw new Error("Unauthorized");
  }
  return res;
}

/* --- LIST PAGE: fetch and render places --- */
document.addEventListener("DOMContentLoaded", async () => {
  const listEl = document.getElementById("places-list");
  if (!listEl) return; // not on index.html

  listEl.innerHTML = "<p>Loading places…</p>";
  try {
    // NOTE: your API expects a trailing slash here
    const res = await apiFetch("/api/v1/places/");
    const places = await res.json();

    if (!Array.isArray(places) || places.length === 0) {
      listEl.innerHTML = "<p>No places yet.</p>";
      return;
    }

    listEl.innerHTML = "";
    places.forEach(p => {
      const card = document.createElement("div");
      card.className = "place-card";
      card.innerHTML = `
        <h3>${p.name}</h3>
        <p>$${p.price_per_night} / night</p>
        <button class="details-button" onclick="location.href='place.html?id=${p.id}'">View Details</button>
      `;
      listEl.appendChild(card);
    });
  } catch (err) {
    listEl.innerHTML = `<p style="color:#b00">Error: ${err.message}</p>`;
  }
});
JS
