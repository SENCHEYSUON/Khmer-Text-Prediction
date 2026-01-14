const input = document.getElementById("input");
const sugs  = document.getElementById("sugs");
const statusEl = document.getElementById("status");
const skeleton = document.getElementById("skeleton");
const toggleTheme = document.getElementById("toggleTheme");
const clearBtn = document.getElementById("clearBtn");

let currentSuggestions = [];

// ---------- Theme ----------
function setTheme(theme){
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
  toggleTheme.textContent = theme === "dark" ? "☀️" : "🌙";
}
const savedTheme = localStorage.getItem("theme") || "light";
setTheme(savedTheme);

toggleTheme.addEventListener("click", () => {
  const now = document.documentElement.getAttribute("data-theme") || "light";
  setTheme(now === "dark" ? "light" : "dark");
});

clearBtn.addEventListener("click", () => {
  input.value = "";
  renderSuggestions([]);
  statusEl.textContent = "Ready";
  input.focus();
});

// ---------- Debounce ----------
function debounce(fn, delay=120){
  let t=null;
  return (...args) => {
    clearTimeout(t);
    t=setTimeout(() => fn(...args), delay);
  };
}

function showLoading(isLoading){
  skeleton.classList.toggle("hidden", !isLoading);
  statusEl.textContent = isLoading ? "Suggesting..." : "Ready";
}

async function fetchSuggestions(text){
  const res = await fetch("/suggest", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({text})
  });
  if(!res.ok) return [];
  const data = await res.json();
  return data.suggestions || [];
}

function insertWord(word){
  const v = input.value || "";
  const needsSpace = v.length > 0 && !/\s$/.test(v);
  input.value = v + (needsSpace ? " " : "") + word + " ";
  input.focus();
  input.dispatchEvent(new Event("input")); // refresh after insert
}

function renderSuggestions(list){
  currentSuggestions = list;
  sugs.innerHTML = "";

  list.forEach((word, i) => {
    const btn = document.createElement("div");
    btn.className = "chip";
    btn.textContent = word;

    const kbd = document.createElement("span");
    kbd.className = "kbd";
    kbd.textContent = `${i+1}`;

    btn.appendChild(kbd);
    btn.onclick = () => insertWord(word);
    sugs.appendChild(btn);
  });
}

// keyboard shortcuts 1–5
document.addEventListener("keydown", (e) => {
  if(e.target !== input) return;
  const k = e.key;
  if(k >= "1" && k <= "5"){
    const idx = parseInt(k, 10) - 1;
    const w = currentSuggestions[idx];
    if(w){
      e.preventDefault();
      insertWord(w);
    }
  }
});

// main input handler
const onInput = debounce(async () => {
  const text = input.value || "";
  if(!text.trim()){
    renderSuggestions([]);
    showLoading(false);
    return;
  }

  showLoading(true);
  try{
    const list = await fetchSuggestions(text);
    renderSuggestions(list);
  } finally {
    showLoading(false);
  }
}, 130);

input.addEventListener("input", onInput);
