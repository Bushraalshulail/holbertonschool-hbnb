/* ---------- tiny helpers ---------- */
function getCookie(name){
  return document.cookie.split("; ").reduce((acc,c)=>{
    const [k,v]=c.split("="); return k===name?decodeURIComponent(v):acc;
  }, "");
}
function setCookie(name, value){
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/`;
}
function qs(name){ return new URLSearchParams(location.search).get(name); }

/* Centralized fetch: auto-attach JWT if present */
async function apiFetch(path, options={}){
  const token = getCookie("token");
  const headers = { "Content-Type":"application/json", ...(options.headers||{}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(path, { ...options, headers });
  return res;
}

/* ---------- page routers ---------- */
document.addEventListener("DOMContentLoaded", async () => {
  const path = location.pathname;

  // Login page
  if (path.endsWith("/login.html") || path.endsWith("login.html")) {
    const form = document.getElementById("login-form");
    if (!form) return;
    form.addEventListener("submit", async (e)=>{
      e.preventDefault();
      const email = document.getElementById("email").value.trim();
      const password = document.getElementById("password").value;
      try{
        // Your API route is /api/v1/auth/login
        const res = await fetch("/api/v1/auth/login", {
          method:"POST",
          headers:{ "Content-Type":"application/json" },
          body: JSON.stringify({ email, password })
        });
        if(!res.ok){
          const txt = await res.text();
          alert("Login failed: " + txt);
          return;
        }
        const data = await res.json();
        setCookie("token", data.access_token);
        location.href = "index.html";
      }catch(err){
        alert("Login error: "+err.message);
      }
    });
    return;
  }

  // Index (List of Places) — requirement: redirect to login if not authenticated
  if (path.endsWith("/index.html") || path.endsWith("/client/") || path.endsWith("/client")) {
    if (!getCookie("token")) { location.href = "login.html"; return; }

    const list = document.getElementById("places-list");
    const $country = document.getElementById("country-filter");
    const $price = document.getElementById("price-filter");

    list.innerHTML = "<p>Loading places…</p>";
    try{
      // Trailing slash matters for your API
      const res = await apiFetch("/api/v1/places/");
      if (!res.ok) throw new Error("Failed to load places: " + res.status);
      const places = await res.json();

      // Populate country filter
      const countries = Array.from(new Set(places.map(p => (p.country||"").trim()).filter(Boolean))).sort();
      countries.forEach(c=>{
        const opt = document.createElement("option");
        opt.value = c; opt.textContent = c;
        $country.appendChild(opt);
      });

      function render(){
        const chosenCountry = $country.value;
        const maxPrice = $price.value === "__all__" ? Infinity : Number($price.value);

        list.innerHTML = "";
        const filtered = places.filter(p=>{
          const inCountry = (chosenCountry==="__all__") || ((p.country||"") === chosenCountry);
          const inPrice = (typeof p.price === "number" ? p.price : Number(p.price)) <= maxPrice;
          return inCountry && inPrice;
        });

        if (!filtered.length){
          list.innerHTML = "<p>No places match the filter.</p>";
          return;
        }

        filtered.forEach(p=>{
          const card = document.createElement("div");
          card.className = "place-card";
          card.innerHTML = `
            <h3>${p.title}</h3>
            <p>$${p.price} / night</p>
            <button class="details-button" onclick="location.href='place.html?id=${p.id}'">View Details</button>
          `;
          list.appendChild(card);
        });
      }

      $country.addEventListener("change", render);
      $price.addEventListener("change", render);
      render();
    }catch(e){
      list.innerHTML = `<p style="color:#b00">Error: ${e.message}</p>`;
    }
    return;
  }

  // Place details page
  if (path.endsWith("/place.html") || path.endsWith("place.html")) {
    const id = qs("id");
    const placeEl = document.getElementById("place");
    const reviewsEl = document.getElementById("reviews");
    const addCta = document.getElementById("addReviewCta");
    const loginLink = document.getElementById("loginLink");

    if (!id){ placeEl.textContent="Missing place id"; return; }
    if (getCookie("token") && loginLink) loginLink.textContent = "Logged In";

    // details
    try{
      const res = await apiFetch(`/api/v1/places/${id}/`); // trailing slash
      if (!res.ok){ placeEl.textContent = `Error ${res.status}`; return; }
      const p = await res.json();
      placeEl.innerHTML = `
        <div class="place-info">
          <h1>${p.title}</h1>
          <p><strong>Price:</strong> $${p.price} / night</p>
          <p><strong>Location:</strong> ${(p.city||"")}${p.country? ", "+p.country:""}</p>
          <p>${p.description || ""}</p>
          <p><strong>Host:</strong> ${p.owner ? (p.owner.first_name+" "+p.owner.last_name) : "—"}</p>
        </div>
      `;
    }catch(e){ placeEl.textContent = "Failed to load place: " + e.message; }

    // reviews (your routes file shows: /api/v1/reviews/places/<place_id>/reviews)
    try{
      const res = await apiFetch(`/api/v1/reviews/places/${id}/reviews`);
      if (res.ok){
        const arr = await res.json();
        if (Array.isArray(arr) && arr.length){
          reviewsEl.innerHTML = "";
          arr.forEach(r=>{
            const div = document.createElement("div");
            div.className = "review-card";
            div.innerHTML = `
              <p>${r.comment || ""}</p>
              <small>By ${r.user ? (r.user.first_name+" "+r.user.last_name) : "Anonymous"} — Rating: ${r.rating ?? "—"}</small>
            `;
            reviewsEl.appendChild(div);
          });
        } else {
          reviewsEl.innerHTML = "<p>No reviews yet.</p>";
        }
      } else {
        reviewsEl.innerHTML = `<p>Couldn’t load reviews (${res.status}).</p>`;
      }
    }catch(e){ reviewsEl.innerHTML = `<p>Error loading reviews: ${e.message}</p>`; }

    // add review button if logged in
    if (getCookie("token")) {
      addCta.innerHTML = `<button class="details-button" onclick="location.href='add_review.html?id=${id}'">Add Review</button>`;
    }
    return;
  }

  // Add Review page
  if (path.endsWith("/add_review.html") || path.endsWith("add_review.html")) {
    if (!getCookie("token")) { location.href = "index.html"; return; }
    const id = qs("id");
    const form = document.getElementById("revForm");
    form.addEventListener("submit", async (e)=>{
      e.preventDefault();
      const payload = {
        place_id: id,
        rating: Number(document.getElementById("rating").value),
        comment: document.getElementById("comment").value.trim()
      };
      try{
        const res = await apiFetch(`/api/v1/reviews/`, {
          method:"POST",
          body: JSON.stringify(payload)
        });
        const data = await res.json().catch(()=>({}));
        if (!res.ok){
          alert((data && (data.message||data.msg||data.error)) || `Error ${res.status}`);
          return;
        }
        location.href = `place.html?id=${id}`;
      }catch(err){ alert("Failed: " + err.message); }
    });
    return;
  }
});
