// Makes the coverage map on the landing pages interactive: hover or tap a country to see its
// status. Without JavaScript the static map image stays as it is.
(() => {
  const box = document.querySelector("[data-map]");
  const img = box && box.querySelector("img");
  if (!img || !window.fetch || !window.DOMParser) return;
  const link = box.querySelector("a");
  const word = k => box.getAttribute("data-map-" + k);
  let names = null;
  try { names = new Intl.DisplayNames([document.documentElement.lang || "en"], {type: "region"}); } catch (e) {}
  // Country name in the page language where the browser knows it; the English name otherwise.
  const label = el => {
    const en = el.getAttribute("data-label"), code = el.getAttribute("data-code") || "";
    const kind = word(el.getAttribute("data-kind"));
    let name = en.split(": ")[0];
    if (names && code.length === 2) {
      try { const n = names.of(code.toUpperCase()); if (n && n.toUpperCase() !== code.toUpperCase()) name = n; } catch (e) {}
    }
    return kind ? name + ": " + kind : en;
  };
  const dark = matchMedia("(prefers-color-scheme: dark)").matches;
  const srcDark = box.querySelector("source") && box.querySelector("source").getAttribute("srcset");
  const src = dark && srcDark ? srcDark : img.getAttribute("src");
  fetch(src).then(r => r.ok ? r.text() : Promise.reject(r.status)).then(text => {
    const svg = new DOMParser().parseFromString(text, "image/svg+xml").documentElement;
    if (svg.nodeName !== "svg") return;
    svg.removeAttribute("width"); svg.removeAttribute("height");
    svg.style.cssText = "display:block;width:100%;height:auto;touch-action:manipulation";
    // Move each shape's <title> into data-label so the browser's own tooltip doesn't double up.
    svg.querySelectorAll("path > title, circle > title, g > title").forEach(t => {
      t.parentNode.setAttribute("data-label", t.textContent); t.remove();
    });
    const tip = document.createElement("div");
    tip.setAttribute("role", "status");
    tip.style.cssText = "min-height:1.6em;margin-top:6px;font-size:15px;text-align:center";
    tip.textContent = word("hint") || "Hover or tap a country to see its coverage.";
    let lit = null;
    const show = e => {
      const el = e.target.closest && e.target.closest("[data-label]");
      if (lit && lit !== el) lit.style.filter = "";
      if (!el) return;
      lit = el; el.style.filter = "brightness(0.8)";
      tip.textContent = label(el);
    };
    svg.addEventListener("pointermove", show);
    svg.addEventListener("pointerdown", show);
    svg.addEventListener("pointerleave", () => { if (lit) lit.style.filter = ""; });
    const full = document.createElement("p");
    full.style.cssText = "text-align:center;margin:4px 0 0";
    full.innerHTML = '<a></a>';
    full.firstChild.href = link ? link.href : "#";
    full.firstChild.textContent = word("table") || "Full coverage table";
    (link || img).replaceWith(svg);
    svg.after(tip, full);
  }).catch(() => {});
})();
