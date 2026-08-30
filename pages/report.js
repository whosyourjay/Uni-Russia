const DATA = JSON.parse(document.getElementById("page-data").textContent);
const $ = selector => document.querySelector(selector);
const SVG = "http://www.w3.org/2000/svg";
const fmt = new Intl.NumberFormat("en-US", {maximumFractionDigits: 0});
const tip = $("#tooltip");

function css(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function esc(value) {
  return String(value ?? "").replace(/[&<>\"]/g, character =>
    ({"&":"&amp;", "<":"&lt;", ">":"&gt;", "\"":"&quot;"}[character]));
}

function add(parent, tag, attributes = {}, text = "") {
  const element = document.createElementNS(SVG, tag);
  Object.entries(attributes).forEach(([name, value]) => element.setAttribute(name, value));
  element.textContent = text;
  parent.append(element);
  return element;
}

function frame(selector, width, height) {
  const svg = $(selector);
  svg.replaceChildren();
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  return svg;
}

function scale(value, low, high, start, stop) {
  return start + (value - low) * (stop - start) / (high - low || 1);
}

function short(value, length = 42) {
  const text = String(value);
  return text.length <= length ? text : `${text.slice(0, length - 1)}…`;
}

function linePath(points) {
  return points.map(([x, y], index) =>
    `${index ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
}

function showTip(event, html) {
  tip.innerHTML = html;
  tip.classList.add("visible");
  tip.style.left = `${Math.min(event.clientX + 13, innerWidth - 365)}px`;
  tip.style.top = `${Math.min(event.clientY + 13, innerHeight - 180)}px`;
}

function hideTip() {
  tip.classList.remove("visible");
}

function hover(element, html) {
  element.addEventListener("mousemove", event => showTip(event,
    typeof html === "function" ? html(event) : html));
  element.addEventListener("mouseleave", hideTip);
}

function legend(target, entries) {
  $(target).innerHTML = entries.map(([label, colour, extra = ""]) =>
    `<span><i class="key" style="background:${colour};${extra}"></i>${esc(label)}</span>`
  ).join("");
}

function xAxis(svg, box, ticks, map, label, format = value => value) {
  add(svg, "line", {x1:box.x0, x2:box.x1, y1:box.y1, y2:box.y1, class:"axis"});
  ticks.forEach(value => {
    const x = map(value);
    add(svg, "line", {x1:x, x2:x, y1:box.y0, y2:box.y1, class:"rule"});
    add(svg, "text", {x, y:box.y1 + 18, "text-anchor":"middle", class:"tick"}, format(value));
  });
  add(svg, "text", {x:(box.x0 + box.x1) / 2, y:box.y1 + 42,
    "text-anchor":"middle", class:"axis-name"}, label);
}

function yAxis(svg, box, ticks, map, label, format = value => value) {
  ticks.forEach(value => {
    const y = map(value);
    add(svg, "line", {x1:box.x0, x2:box.x1, y1:y, y2:y, class:"rule"});
    add(svg, "text", {x:box.x0 - 9, y:y + 3, "text-anchor":"end", class:"tick"}, format(value));
  });
  add(svg, "text", {x:16, y:(box.y0 + box.y1) / 2,
    transform:`rotate(-90 16 ${(box.y0 + box.y1) / 2})`,
    "text-anchor":"middle", class:"axis-name"}, label);
}

function clipGroup(svg, id, box) {
  const definitions = add(svg, "defs");
  const clipPath = add(definitions, "clipPath", {id});
  add(clipPath, "rect", {x:box.x0, y:box.y0,
    width:box.x1 - box.x0, height:box.y1 - box.y0});
  return add(svg, "g", {"clip-path":`url(#${id})`});
}

function bviFigure() {
  const data = DATA.bvi;
  const svg = frame("#bvi-svg", 1040, 590);
  const box = {x0:325, x1:790, y0:28, y1:535};
  const low = Math.max(0, Math.floor((Math.min(...data.rows.map(row => row.proxy)) - 2) / 5) * 5);
  const map = value => scale(value, low, 100, box.x0, box.x1);
  const ticks = Array.from({length:(100 - low) / 5 + 1}, (_, index) => low + index * 5);
  const rowHeight = (box.y1 - box.y0) / data.rows.length;
  add(svg, "rect", {x:map(90), y:box.y0, width:map(100) - map(90),
    height:box.y1 - box.y0, fill:css("--blue"), opacity:.055});
  xAxis(svg, box, ticks, map, "percentile of the ЕГЭ reference cohort");
  data.rows.forEach((row, index) => {
    const y = box.y0 + (index + .5) * rowHeight;
    const share = 100 * row.bvi / row.students;
    add(svg, "text", {x:box.x0 - 12, y:y + 4, "text-anchor":"end", class:"row-name"},
      short(row.school, 43));
    const line = add(svg, "line", {x1:map(row.proxy), x2:map(row.published), y1:y, y2:y,
      stroke:css("--brown"), "stroke-width":2.4, opacity:.8});
    add(svg, "circle", {cx:map(row.published), cy:y, r:5, fill:css("--card"),
      stroke:css("--brown"), "stroke-width":2});
    const point = add(svg, "circle", {cx:map(row.proxy), cy:y, r:5.2,
      fill:css("--blue"), stroke:css("--card"), "stroke-width":1});
    add(svg, "text", {x:807, y:y + 4, class:"annotation"},
      `−${row.shift.toFixed(1)} pts · ${fmt.format(row.bvi)} БВИ (${share.toFixed(0)}%)`);
    const detail = `<b>${esc(row.school)}</b><br>Published percentile: ${row.published.toFixed(1)}` +
      `<br>De-placeholdered proxy: ${row.proxy.toFixed(1)}<br>` +
      `${fmt.format(row.bvi)} of ${fmt.format(row.students)} budget admits were БВИ`;
    hover(line, detail);
    hover(point, detail);
  });
  $("#bvi-year").textContent = data.year;
  $("#bvi-total").textContent = fmt.format(data.total);
  $("#bvi-count").textContent = fmt.format(data.rows.length);
  $("#bvi-largest").textContent = `${data.largestShift.toFixed(1)} pts`;
  legend("#bvi-legend", [["published mean, including nominal 100s", "transparent",
    `border-radius:50%;border:2px solid ${css("--brown")}`],
    ["proxy after removing placeholders", css("--blue"), "border-radius:50%"]]);
}

function fundingCallouts(svg, rows) {
  add(svg, "text", {x:730, y:75, class:"panel-name"}, "Largest consequential gaps");
  add(svg, "text", {x:730, y:96, class:"tick"}, "gap × √seats, one label per school");
  rows.forEach((row, index) => {
    const y = 135 + index * 112;
    const colour = row.gap >= 0 ? css("--blue") : css("--orange");
    add(svg, "circle", {cx:738, cy:y - 4, r:4.5, fill:colour});
    add(svg, "text", {x:751, y, class:"row-name"}, short(row.school, 31));
    add(svg, "text", {x:751, y:y + 18, class:"tick"}, short(row.field, 34));
    add(svg, "text", {x:751, y:y + 39, fill:colour, class:"axis-name"},
      `${row.gap >= 0 ? "+" : ""}${row.gap.toFixed(1)} pts · ${fmt.format(row.seats)} seats`);
  });
}

function fundingFigure() {
  const data = DATA.funding;
  const svg = frame("#funding-svg", 1040, 725);
  const box = {x0:72, x1:692, y0:38, y1:658};
  const x = value => scale(value, 0, 100, box.x0, box.x1);
  const y = value => scale(value, 0, 100, box.y1, box.y0);
  add(svg, "polygon", {points:`${box.x0},${box.y1} ${box.x0},${box.y0} ${box.x1},${box.y0}`,
    fill:css("--blue"), opacity:.045});
  add(svg, "polygon", {points:`${box.x0},${box.y1} ${box.x1},${box.y1} ${box.x1},${box.y0}`,
    fill:css("--orange"), opacity:.045});
  const ticks = [0, 20, 40, 60, 80, 100];
  xAxis(svg, box, ticks, x, "paid-list ability percentile");
  yAxis(svg, box, ticks, y, "budget-list ability percentile");
  add(svg, "line", {x1:box.x0, y1:box.y1, x2:box.x1, y2:box.y0,
    stroke:css("--faint"), "stroke-width":1.2, "stroke-dasharray":"5 4"});
  add(svg, "text", {x:95, y:65, fill:css("--blue"), class:"axis-name"}, "budget list higher");
  add(svg, "text", {x:670, y:638, fill:css("--orange"), "text-anchor":"end",
    class:"axis-name"}, "paid list higher");
  const points = clipGroup(svg, "funding-clip", box);
  data.rows.slice().sort((a, b) => b.seats - a.seats).forEach(row => {
    const colour = row.gap >= 0 ? css("--blue") : css("--orange");
    const radius = Math.max(1.3, Math.min(7, Math.sqrt(row.seats) / 5));
    const point = add(points, "circle", {cx:x(row.paid), cy:y(row.budget), r:radius,
      fill:colour, opacity:.38, stroke:css("--card"), "stroke-width":.35});
    hover(point, `<b>${esc(row.school)}</b><br>${esc(row.field)}<br>` +
      `Budget: ${row.budget.toFixed(1)}th percentile<br>Paid: ${row.paid.toFixed(1)}th percentile` +
      `<br>Gap: ${row.gap >= 0 ? "+" : ""}${row.gap.toFixed(1)} points · ${fmt.format(row.seats)} seats`);
  });
  fundingCallouts(svg, data.labels);
  $("#funding-year").textContent = data.year;
  $("#funding-count").textContent = fmt.format(data.rows.length);
  $("#funding-seats").textContent = fmt.format(data.seats);
  $("#funding-higher").textContent = `${data.higherPercent.toFixed(0)}%`;
  $("#funding-gap").textContent = `${data.medianGap >= 0 ? "+" : ""}${data.medianGap.toFixed(1)} pts`;
  legend("#funding-legend", [["budget list higher", css("--blue")],
    ["paid list higher", css("--orange")], ["same selectivity", css("--faint")]]);
}

function coverageFigure() {
  const data = DATA.coverage;
  const svg = frame("#coverage-svg", 1040, 590);
  const x0 = 182, y0 = 54, cellWidth = 89, cellHeight = 34;
  const colours = [css("--empty"), css("--grey"), css("--tan"),
    css("--blue"), css("--blue-deep")];
  data.years.forEach((year, index) => add(svg, "text", {
    x:x0 + (index + .5) * cellWidth, y:28, "text-anchor":"middle", class:"tick"}, year));
  data.subjects.forEach((subject, rowIndex) => {
    const y = y0 + rowIndex * cellHeight;
    add(svg, "text", {x:x0 - 13, y:y + 21, "text-anchor":"end", class:"row-name"}, subject[1]);
    data.matrix[rowIndex].forEach((level, columnIndex) => {
      const x = x0 + columnIndex * cellWidth;
      const cell = add(svg, "rect", {x:x + 1, y:y + 1, width:cellWidth - 2,
        height:cellHeight - 2, rx:2, fill:colours[level]});
      if (level === 1) add(svg, "text", {x:x + cellWidth / 2, y:y + 22,
        "text-anchor":"middle", fill:css("--card"), "font-size":15}, "•");
      if (level === 4) add(svg, "text", {x:x + cellWidth / 2, y:y + 21,
        "text-anchor":"middle", fill:"white", "font-size":9, "font-weight":600}, "curve");
      hover(cell, `<b>${esc(subject[1])} · ${data.years[columnIndex]}</b><br>${esc(data.labels[level])}`);
    });
  });
  const modelY = y0 + data.subjects.length * cellHeight + 58;
  add(svg, "text", {x:x0 - 13, y:modelY + 19, "text-anchor":"end", class:"row-name"}, "CDF used");
  data.model.forEach((row, index) => {
    const x = x0 + index * cellWidth + 7;
    const colour = row.carried ? css("--brown") : css("--green");
    const cell = add(svg, "rect", {x, y:modelY, width:cellWidth - 14, height:35,
      rx:3, fill:colour, opacity:.18, stroke:colour, "stroke-width":1.2});
    const label = row.carried ? `← ${row.distributionYear}` : `${row.subjects} subj.`;
    add(svg, "text", {x:x + (cellWidth - 14) / 2, y:modelY + 22,
      "text-anchor":"middle", fill:colour, "font-size":9.5, "font-weight":600}, label);
    hover(cell, `<b>Model year ${row.year}</b><br>` + (row.carried ?
      `Carries the ${row.distributionYear} distribution` :
      `Uses ${row.subjects} recovered subject distribution${row.subjects === 1 ? "" : "s"}`));
  });
  add(svg, "text", {x:x0, y:modelY - 16, fill:css("--brown"), class:"tick"},
    "2011–16 also carry → 2017");
  $("#coverage-recovered").textContent = fmt.format(data.recovered);
  $("#coverage-curves").textContent = fmt.format(data.curves);
  $("#coverage-carried").textContent = `${data.carriedYears} / ${data.years.length}`;
  legend("#coverage-legend", [[data.labels[1], colours[1]], [data.labels[2], colours[2]],
    [data.labels[3], colours[3]], [data.labels[4], colours[4]],
    ["observed model year", css("--green")], ["carried model year", css("--brown")]]);
}

function spoFigure() {
  const data = DATA.spo;
  const svg = frame("#spo-svg", 1040, 630);
  const box = {x0:80, x1:970, y0:34, y1:556};
  const x = value => scale(Math.log(value), Math.log(.9), Math.log(85), box.x0, box.x1);
  const y = value => scale(value, 2.65, 5.05, box.y1, box.y0);
  const xTicks = [1, 2, 5, 10, 20, 50];
  const yTicks = [3, 3.5, 4, 4.5, 5];
  xAxis(svg, box, xTicks, x, "applications per budget place · log scale");
  yAxis(svg, box, yTicks, y, "mean certificate GPA of budget entrants",
    value => value.toFixed(1));
  add(svg, "line", {x1:box.x0, x2:box.x1, y1:y(4), y2:y(4),
    stroke:css("--faint"), "stroke-width":1.1, "stroke-dasharray":"5 4"});
  add(svg, "text", {x:box.x0 + 7, y:y(4) - 8, class:"tick"}, "4.0 certificate average");
  const points = clipGroup(svg, "spo-clip", box);
  data.rows.slice().sort((a, b) => Number(a.gap !== null) - Number(b.gap !== null)).forEach(row => {
    const colour = row.gap === null ? css("--grey") :
      (row.gap >= 0 ? css("--blue") : css("--orange"));
    const point = add(points, "circle", {cx:x(row.applications), cy:y(row.gpa), r:2.5,
      fill:colour, opacity:row.gap === null ? .3 : .48});
    const gap = row.gap === null ? "Paid entrant GPA unavailable" :
      `Budget minus paid GPA: ${row.gap >= 0 ? "+" : ""}${row.gap.toFixed(2)}`;
    hover(point, `<b>${esc(row.school)}</b><br>${row.applications.toFixed(2)} applications per budget place` +
      `<br>Budget entrant GPA: ${row.gpa.toFixed(2)}<br>${gap}`);
  });
  const trend = data.trend.map(([applications, gpa]) => [x(applications), y(gpa)]);
  add(svg, "path", {d:linePath(trend), fill:"none", stroke:css("--ink"),
    "stroke-width":2.5, "stroke-linejoin":"round"});
  trend.forEach(([cx, cy]) => add(svg, "circle", {cx, cy, r:4,
    fill:css("--ink"), stroke:css("--card"), "stroke-width":1}));
  $("#spo-year").textContent = data.year;
  $("#spo-count").textContent = fmt.format(data.rows.length);
  $("#spo-pages").textContent = `${fmt.format(data.downloaded)} / ${fmt.format(data.indexed)}`;
  $("#spo-paired").textContent = fmt.format(data.paired);
  $("#spo-higher").textContent = `${data.higherPercent.toFixed(0)}%`;
  legend("#spo-legend", [["budget GPA higher", css("--blue")],
    ["paid GPA higher", css("--orange")], ["paid GPA unavailable", css("--grey")],
    ["median within demand band", css("--ink")]]);
}

function renderAll() {
  bviFigure();
  fundingFigure();
  coverageFigure();
  spoFigure();
}

function setupTheme() {
  const root = document.documentElement;
  try {
    const saved = localStorage.getItem("uni-report-theme");
    if (saved === "light" || saved === "dark") root.dataset.theme = saved;
  } catch (_) { /* Storage can be disabled for local files. */ }
  const button = $("#theme");
  const label = () => button.textContent = root.dataset.theme === "dark" ?
    "Use light theme" : "Use dark theme";
  label();
  button.addEventListener("click", () => {
    root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
    try { localStorage.setItem("uni-report-theme", root.dataset.theme); } catch (_) { /* no-op */ }
    label();
    renderAll();
  });
}

function setupNavigation() {
  const links = [...document.querySelectorAll("nav a")];
  const sections = links.map(link => $(link.getAttribute("href")));
  const observer = new IntersectionObserver(entries => {
    entries.filter(entry => entry.isIntersecting).forEach(entry => {
      links.forEach(link => link.classList.toggle("on",
        link.getAttribute("href") === `#${entry.target.id}`));
    });
  }, {rootMargin:"-15% 0px -65% 0px"});
  sections.forEach(section => observer.observe(section));
}

setupTheme();
renderAll();
setupNavigation();
