
const CELEBRANT = {
  name: "Ate Emma Jane Guerra",
  date: "August 20, 2025", 
  heroMessages: [
    "TYSM for being our ate and being selfless sa amin, in my eyes and heart you are the most beautiful and wonderful woman. The world is so cruel sa'yo so please be kind to yourself always<3. Don't worry if yayaman ako we will celebrate your birthday always. Love-ading SZA 🎂",
  ],
  gallery: [
    { src: "assets/ate.jpg", alt: "Memory 1" },
    { src: "assets/ate1.jpg", alt: "Memory 2" },
    { src: "assets/ate2.jpg", alt: "Memory 3" },
    { src: "assets/ate3.jpg", alt: "Memory 4" },
    { src: "assets/ate4.jpg", alt: "Memory 5" },
    { src: "assets/ate5.jpg", alt: "Memory 6" },
  ],
  wishes: [
     { from: "SZA", text: "Kumain lagi sa tamang oras, wag ka nang umiyak sa mga nang-bobody shame sayo.And i hope you find strength and passion in everything that you do." },
    { from: "Karl", text: "Sana makapasa ka sa Masteral mo ate!!" },
    { from: "Ason", text: "successful dreams!" },
  ],
  music: "assets/bg-music.mp3",
};

/* -------------------------------------------------------
 * Helpers
 * ----------------------------------------------------- */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
const pad = (n) => String(Math.floor(n)).padStart(2, "0");
const fmtTime = (s) => `${Math.floor(s / 60)}:${pad(s % 60)}`;

/* Persistent keys */
const LS_WISHES = "bd_wishes";
const LS_VOLUME = "bd_volume";
const LS_THEME = "bd_theme";
const LS_GLOW = "bd_glow";

/* Motion preference */
const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* -------------------------------------------------------
 * Init content
 * ----------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  // Titles
  $("#topbarTitle").textContent = `Happy Birthday, ${CELEBRANT.name}!`;
  $("#heroTitle").textContent = `Happy Birthday, ${CELEBRANT.name}!`;
  $("#footerName").textContent = CELEBRANT.name || "you";
  document.title = `Happy Birthday, ${CELEBRANT.name}!`;
  $("#heroDate").textContent = CELEBRANT.date;

  // Theme + glow
  const savedTheme = localStorage.getItem(LS_THEME);
  if (savedTheme === "light" || savedTheme === "dark") {
    document.documentElement.setAttribute("data-theme", savedTheme);
    $("#themeToggle").setAttribute("aria-pressed", savedTheme === "dark" ? "true" : "false");
  }
  const savedGlow = localStorage.getItem(LS_GLOW);
  if (savedGlow === "off") {
    document.documentElement.setAttribute("data-glow", "off");
    $("#glowToggle").setAttribute("aria-pressed", "true");
  }

  // Typewriter
  initTypewriter(CELEBRANT.heroMessages);

  // Gallery
  buildGallery(CELEBRANT.gallery);

  // Wishes
  initWishes(CELEBRANT.wishes);

  // Player
  initPlayer();

  // Confetti
  initConfetti();

  // Scroll reveal observer
  initReveals();

  // Lightbox
  initLightbox();

  // Finale fireworks
  initFireworks();

  // UI toggles
  initToggles();

  // Print
  $("#printBtn").addEventListener("click", () => window.print());
});

/* -------------------------------------------------------
 * Typewriter (rotates messages)
 * ----------------------------------------------------- */
function initTypewriter(lines = []) {
  const el = $("#typewriter");
  if (!el || !lines.length) return;
  let idx = 0, char = 0, deleting = false, pause = 1000, timer;

  const speed = prefersReduced ? 30 : 45;

  function tick() {
    const text = lines[idx];
    if (!deleting) {
      char++;
      el.textContent = text.slice(0, char);
      if (char === text.length) {
        deleting = true;
        timer = setTimeout(tick, pause);
        return;
      }
    } else {
      char--;
      el.textContent = text.slice(0, char);
      if (char === 0) {
        deleting = false;
        idx = (idx + 1) % lines.length;
      }
    }
    timer = setTimeout(tick, speed);
  }
  tick();
}

/* -------------------------------------------------------
 * Gallery + Parallax Hover + Lightbox hooks
 * ----------------------------------------------------- */
function buildGallery(items = []) {
  const grid = $("#galleryGrid");
  if (!grid) return;

  const isTouch = matchMedia("(hover: none)").matches;

  items.forEach((item, i) => {
    const card = document.createElement("figure");
    card.className = "gallery__item reveal cardless";
    card.tabIndex = 0;

    const img = document.createElement("img");
    img.src = item.src;
    img.alt = item.alt || `Photo ${i + 1}`;
    img.loading = "lazy";
    img.decoding = "async";

    const caption = document.createElement("figcaption");
    caption.className = "gallery__caption";
    caption.textContent = item.alt || `Memory ${i + 1}`;

    card.append(img, caption);
    grid.append(card);

    // Open lightbox on click/Enter/Space
    card.addEventListener("click", () => openLightbox(i));
    card.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault(); openLightbox(i);
      }
    });

    // Subtle parallax on hover (disabled on touch / reduced motion)
    if (!isTouch && !prefersReduced) {
      card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const mx = (e.clientX - rect.left) / rect.width - 0.5;
        const my = (e.clientY - rect.top) / rect.height - 0.5;
        img.style.transform = `scale(1.06) translate(${mx * 6}px, ${my * 6}px)`;
      });
      card.addEventListener("mouseleave", () => (img.style.transform = ""));
    }
  });
}

/* -------------------------------------------------------
 * Lightbox (keyboard + swipe)
 * ----------------------------------------------------- */
let LB = { open: false, idx: 0, items: CELEBRANT.gallery, startX: 0, endX: 0 };
function initLightbox() {
  const lb = $("#lightbox");
  const img = $("#lightboxImage");
  const cap = $("#lightboxCaption");

  $("#lightboxClose").addEventListener("click", closeLightbox);
  $("#lightboxPrev").addEventListener("click", () => stepLightbox(-1));
  $("#lightboxNext").addEventListener("click", () => stepLightbox(1));

  lb.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") stepLightbox(-1);
    if (e.key === "ArrowRight") stepLightbox(1);
  });

  // Swipe
  lb.addEventListener("touchstart", (e) => (LB.startX = e.changedTouches[0].clientX));
  lb.addEventListener("touchend", (e) => {
    LB.endX = e.changedTouches[0].clientX;
    const dx = LB.endX - LB.startX;
    if (Math.abs(dx) > 40) stepLightbox(dx > 0 ? -1 : 1);
  });

  // trap focus when open
  lb.addEventListener("keydown", (e) => {
    if (e.key !== "Tab") return;
    const f = $$("#lightbox button");
    if (!f.length) return;
    const first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  function render() {
    const item = LB.items[LB.idx];
    img.src = item.src;
    img.alt = item.alt || `Photo ${LB.idx + 1}`;
    cap.textContent = item.alt || "";
  }

  window.openLightbox = (i) => {
    LB.idx = i;
    render();
    lb.setAttribute("aria-hidden", "false");
    LB.open = true;
    lb.style.display = "grid";
    lb.focus();
    $("#lightboxClose").focus();
  };

  window.closeLightbox = () => {
    lb.setAttribute("aria-hidden", "true");
    LB.open = false;
    lb.style.display = "none";
  };

  window.stepLightbox = (d) => {
    LB.idx = (LB.idx + d + LB.items.length) % LB.items.length;
    render();
  };
}

/* -------------------------------------------------------
 * Wishes (render + modal with focus trap + localStorage)
 * ----------------------------------------------------- */
function initWishes(initial = []) {
  const stored = JSON.parse(localStorage.getItem(LS_WISHES) || "[]");
  const data = [...initial, ...stored];
  const wall = $("#messageWall");

  const render = () => {
    wall.innerHTML = "";
    data.forEach((w) => {
      const card = document.createElement("article");
      card.className = "card reveal";
      card.innerHTML = `
        <h4 class="card__from">${escapeHTML(w.from)} <span aria-hidden="true">💌</span></h4>
        <p class="card__text">${escapeHTML(w.text)}</p>
      `;
      wall.append(card);
    });
    // re-observe for reveal
    if (revealObserver) $$(".reveal").forEach((el) => revealObserver.observe(el));
  };

  render();

  // Modal controls
  const modal = $("#wishModal");
  const backdrop = $("#modalBackdrop");
  const openBtn = $("#addWishBtn");
  const closeBtn = $("#wishClose");
  const cancelBtn = $("#wishCancel");
  const form = $("#wishForm");
  const nameInput = $("#wishName");
  const textInput = $("#wishText");

  const openModal = () => {
    modal.setAttribute("aria-hidden", "false");
    backdrop.hidden = false;
    modal.style.display = "grid";
    nameInput.value = ""; textInput.value = "";
    // Focus trap
    const focusables = $$("#wishModal button, #wishModal input, #wishModal textarea");
    const first = focusables[0], last = focusables[focusables.length - 1];
    modal.addEventListener("keydown", trap);
    function trap(e) {
      if (e.key === "Escape") return closeModal();
      if (e.key !== "Tab") return;
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
    nameInput.focus();
  };

  const closeModal = () => {
    modal.setAttribute("aria-hidden", "true");
    backdrop.hidden = true;
    modal.style.display = "none";
    openBtn.focus();
  };

  openBtn.addEventListener("click", openModal);
  closeBtn.addEventListener("click", closeModal);
  cancelBtn.addEventListener("click", closeModal);
  backdrop.addEventListener("click", closeModal);

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const from = nameInput.value.trim() || "Friend";
    const text = textInput.value.trim();
    if (!text) return;
    const wish = { from, text };
    data.push(wish);
    const newOnes = data.slice(CELEBRANT.wishes.length);
    localStorage.setItem(LS_WISHES, JSON.stringify(newOnes));
    render();
    closeModal();
  });
}

function escapeHTML(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c]));
}

/* -------------------------------------------------------
 * Player (no autoplay with sound; user-initiated)
 * ----------------------------------------------------- */
function initPlayer() {
  const audio = $("#bgAudio");
  audio.src = CELEBRANT.music;

  const playPause = $("#playPause");
  const muteToggle = $("#muteToggle");
  const volume = $("#volume");
  const seek = $("#seek");
  const status = $("#musicStatus");
  const currentTimeEl = $("#currentTime");
  const durationEl = $("#duration");

  let seeking = false;

  // initial states
  audio.volume = parseFloat(localStorage.getItem(LS_VOLUME) || "0.5");
  volume.value = String(audio.volume);
  audio.muted = true; // do not autoplay with sound
  updateStatus();

  playPause.addEventListener("click", async () => {
    try {
      if (audio.paused) {
        audio.muted = false; // user gesture enables sound
        await audio.play();
      } else {
        audio.pause();
      }
      updateStatus();
    } catch (e) {
      // Autoplay policy may still block; stay muted but consider as playing silently
      console.warn(e);
    }
  });

  muteToggle.addEventListener("click", () => {
    audio.muted = !audio.muted;
    updateStatus();
  });

  volume.addEventListener("input", () => {
    audio.volume = parseFloat(volume.value);
    localStorage.setItem(LS_VOLUME, String(audio.volume));
    if (audio.volume > 0 && audio.muted) audio.muted = false;
    updateStatus();
  });

  audio.addEventListener("timeupdate", () => {
    if (!seeking && audio.duration) {
      seek.value = String((audio.currentTime / audio.duration) * 100);
      currentTimeEl.textContent = fmtTime(audio.currentTime | 0);
    }
  });

  audio.addEventListener("loadedmetadata", () => {
    durationEl.textContent = fmtTime(audio.duration | 0);
  });

  seek.addEventListener("input", () => {
    seeking = true;
  });
  seek.addEventListener("change", () => {
    if (audio.duration) {
      audio.currentTime = (parseFloat(seek.value) / 100) * audio.duration;
    }
    seeking = false;
  });

  function updateStatus() {
    const state = audio.paused ? "paused" : "playing";
    playPause.dataset.state = state;
    playPause.innerHTML = state === "playing" ? "⏸️ <span class='sr-only'>Pause</span>" : "▶️ <span class='sr-only'>Play</span>";
    muteToggle.textContent = audio.muted || audio.volume === 0 ? "🔇" : "🔈";
    status.textContent = state === "playing" ? (audio.muted || audio.volume === 0 ? "Music playing (muted)" : "Music on") : "Music off";
  }
}

/* -------------------------------------------------------
 * Confetti (lightweight particles)
 * ----------------------------------------------------- */
function initConfetti() {
  const canvas = $("#confettiCanvas");
  const ctx = canvas.getContext("2d");
  let w, h, rafId, running = true, startTime = performance.now();

  const colors = ["#5de4ff", "#ff6ac1", "#a78bfa", "#ffffff"];
  const count = prefersReduced ? 60 : 160;
  let parts = [];

  const resize = () => {
    w = canvas.width = canvas.offsetWidth;
    h = canvas.height = canvas.offsetHeight;
  };
  resize();
  window.addEventListener("resize", resize);

  for (let i = 0; i < count; i++) {
    parts.push({
      x: Math.random() * w,
      y: Math.random() * -h,
      r: Math.random() * 5 + 2,
      c: colors[(Math.random() * colors.length) | 0],
      vy: Math.random() * 1.5 + 1,
      vx: (Math.random() - 0.5) * 1.2,
      rot: Math.random() * Math.PI,
    });
  }

  function draw(t) {
    if (document.hidden || prefersReduced) return; // throttle if hidden or reduced
    ctx.clearRect(0, 0, w, h);
    for (const p of parts) {
      p.x += p.vx;
      p.y += p.vy;
      p.rot += 0.02;
      if (p.y - p.r > h) { p.y = -10; p.x = Math.random() * w; }
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rot);
      ctx.fillStyle = p.c;
      ctx.fillRect(-p.r, -p.r, p.r * 2, p.r * 2);
      ctx.restore();
    }
    rafId = requestAnimationFrame(draw);
  }

  
  // run ~8s then stop; allow replay
  const runDuration = prefersReduced ? 2000 : 8000;
  const tick = () => {
    const now = performance.now();
    if (now - startTime < runDuration && running) {
      rafId = requestAnimationFrame(draw);
    } else {
      cancelAnimationFrame(rafId);
      running = false;
      $("#confettiReplay").hidden = false;
    }
  };
  rafId = requestAnimationFrame(draw);
  const stopTimer = setInterval(tick, 200);

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAnimationFrame(rafId);
    } else if (!running) {
      // stay stopped
    } else {
      rafId = requestAnimationFrame(draw);
    }
  });

  $("#confettiReplay").addEventListener("click", () => {
    startTime = performance.now();
    running = true;
    $("#confettiReplay").hidden = true;
    rafId = requestAnimationFrame(draw);
  });
}

/* -------------------------------------------------------
 * Scroll reveal (IntersectionObserver)
 * ----------------------------------------------------- */
let revealObserver;
function initReveals() {
  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  $$(".reveal").forEach((el) => revealObserver.observe(el));
}

/* -------------------------------------------------------
 * Fireworks (click bursts)
 * ----------------------------------------------------- */
function initFireworks() {
  const canvas = document.getElementById("fireworksCanvas"); // ✅ get canvas properly
  const ctx = canvas.getContext("2d");
  let w, h, parts = [], rafId;

  // Handle reduced motion (if user prefers less animations)
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = w = rect.width;
    canvas.height = h = Math.max(rect.height, 220);
  }
  resize();
  window.addEventListener("resize", resize);

  function burst(x, y) {
    const N = prefersReduced ? 18 : 36;
    for (let i = 0; i < N; i++) {
      const a = (i / N) * Math.PI * 2;
      const speed = 2 + Math.random() * 2.5;
      parts.push({
        x, y,
        vx: Math.cos(a) * speed,
        vy: Math.sin(a) * speed,
        life: 60 + Math.random() * 30,
        c: i % 3 === 0 ? "#5de4ff" : i % 3 === 1 ? "#ff6ac1" : "#a78bfa",
      });
    }
    if (!rafId) rafId = requestAnimationFrame(draw);
  }

  function draw() {
    if (document.hidden || prefersReduced) { rafId = null; return; }
    ctx.fillStyle = "rgba(0,0,0,0.25)";
    ctx.fillRect(0, 0, w, h);
    parts = parts.filter((p) => p.life > 0);
    for (const p of parts) {
      p.x += p.vx; 
      p.y += p.vy; 
      p.vy += 0.03; 
      p.life--;
      ctx.beginPath(); 
      ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
      ctx.fillStyle = p.c; 
      ctx.fill();
    }
    if (parts.length) rafId = requestAnimationFrame(draw);
    else rafId = null;
  }

  const rectPos = (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX || e.touches?.[0]?.clientX) - rect.left;
    const y = (e.clientY || e.touches?.[0]?.clientY) - rect.top;
    return { x, y };
  };

  canvas.addEventListener("click", (e) => burst(...Object.values(rectPos(e))));
  canvas.addEventListener("touchstart", (e) => { 
    e.preventDefault(); 
    burst(...Object.values(rectPos(e))); 
  }, { passive: false });
}



/* -------------------------------------------------------
 * Theme + Glow toggles
 * ----------------------------------------------------- */
function initToggles() {
  const themeBtn = $("#themeToggle");
  themeBtn.addEventListener("click", () => {
    const html = document.documentElement;
    const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark";
    html.setAttribute("data-theme", next);
    themeBtn.setAttribute("aria-pressed", next === "dark" ? "true" : "false");
    localStorage.setItem(LS_THEME, next);
  });

  const glowBtn = $("#glowToggle");
  glowBtn.addEventListener("click", () => {
    const html = document.documentElement;
    const off = html.getAttribute("data-glow") === "off" ? null : "off";
    if (off) { html.setAttribute("data-glow", "off"); glowBtn.setAttribute("aria-pressed", "true"); }
    else { html.removeAttribute("data-glow"); glowBtn.setAttribute("aria-pressed", "false"); }
    localStorage.setItem(LS_GLOW, off ? "off" : "on");
  });
}
