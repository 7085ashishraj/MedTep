// No browser credentials or form values are read by these isolated UI checks.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const code = fs.readFileSync(path.join(__dirname, "..", "static/js/site.js"), "utf8");
const css = fs.readFileSync(path.join(__dirname, "..", "static/css/theme.css"), "utf8");

function element() {
  return { events: {}, attributes: {}, hidden: true, dataset: {}, classes: new Set(),
    addEventListener(name, callback) { this.events[name] = callback; },
    getAttribute(name) { return this.attributes[name]; },
    setAttribute(name, value) { this.attributes[name] = value; },
    focus() { this.focused = true; },
    scrollIntoView(options) { this.scrolled = options; },
  };
}
function fixture({ bootstrap = true, withSummary = true, passwordTarget = true } = {}) {
  const summary = element(), menu = element(), menuButton = element(), field = element();
  const password = element(), toggle = element(), html = element();
  field.type = "text"; password.type = "password";
  const outer = { open: false, parentElement: null };
  const inner = { open: false, parentElement: { closest: () => outer } };
  field.closest = () => inner;
  menu.classes.add("show");
  menu.classList = { contains: (name) => menu.classes.has(name) };
  html.classes.add("no-js");
  html.classList = { remove: (name) => html.classes.delete(name) };
  menu.contains = (node) => node === menu;
  menuButton.contains = (node) => node === menuButton;
  toggle.attributes["aria-controls"] = "id_password";
  toggle.dataset.passwordLabel = "Password confirmation";
  const nodes = { "form-error-summary": withSummary ? summary : null, "main-navigation": menu,
    "id_field": field, "id_password": passwordTarget ? password : null };
  let hideCount = 0;
  const documentEvents = {};
  vm.runInNewContext(code, {
    window: bootstrap ? { bootstrap: { Collapse: {
      getOrCreateInstance: () => ({ hide() { hideCount += 1; menu.classes.delete("show"); } }),
    } } } : {},
    document: {
      documentElement: html, getElementById: (id) => nodes[id],
      querySelector: () => menuButton, querySelectorAll: () => [toggle],
      addEventListener: (name, callback) => { documentEvents[name] = callback; },
    },
  });
  return { summary, menu, menuButton, field, password, toggle, html, inner, outer,
    documentEvents, get hideCount() { return hideCount; } };
}

let count = 0;
function test(name, run) { run(); count += 1; console.log(`PASS ${name}`); }
test("navigation keeps the no-script fallback until Bootstrap is available", () => {
  assert.equal(fixture({ bootstrap: false }).html.classes.has("no-js"), true);
  assert.equal(fixture().html.classes.has("no-js"), false);
});
test("error summaries focus on load and open nested details before field focus", () => {
  const state = fixture();
  assert.equal(state.summary.focused, true);
  const link = { getAttribute: () => "#id_field" };
  state.summary.events.click({ target: { closest: () => link }, preventDefault() {} });
  assert.equal(state.inner.open, true);
  assert.equal(state.outer.open, true);
  assert.equal(state.field.focused, true);
  assert.equal(state.field.scrolled.behavior, "instant");
});
test("missing and hidden error targets are ignored safely", () => {
  const state = fixture(); state.field.type = "hidden";
  state.summary.events.click({ target: { closest: () => ({ getAttribute: () => "#id_field" }) }, preventDefault() {} });
  assert.equal(state.field.focused, undefined);
  state.summary.events.click({ target: { closest: () => ({ getAttribute: () => "#missing" }) }, preventDefault() {} });
});
test("Escape closes expanded navigation and returns focus to its button", () => {
  const state = fixture();
  state.menu.events.keydown({ key: "Escape", preventDefault() {} });
  assert.equal(state.hideCount, 1);
  assert.equal(state.menuButton.focused, true);
  state.menu.events.keydown({ key: "Escape", preventDefault() {} });
  assert.equal(state.hideCount, 1);
});
test("tabbing into page content closes the menu without stealing focus", () => {
  const state = fixture();
  state.documentEvents.focusin({ target: state.menu });
  assert.equal(state.hideCount, 0);
  state.documentEvents.focusin({ target: state.field });
  assert.equal(state.hideCount, 1);
  assert.equal(state.menuButton.focused, undefined);
});
test("password buttons change visibility and accessible labels without reading values", () => {
  const state = fixture();
  assert.equal(state.toggle.hidden, false);
  state.toggle.events.click();
  assert.equal(state.password.type, "text");
  assert.equal(state.toggle.attributes["aria-label"], "Hide password confirmation");
  state.toggle.events.click();
  assert.equal(state.password.type, "password");
  assert.equal(state.toggle.attributes["aria-label"], "Show password confirmation");
});
test("pages without a summary or matching password target remain usable", () => {
  assert.equal(fixture({ withSummary: false, passwordTarget: false }).toggle.hidden, true);
});

function color(name) {
  const match = css.match(new RegExp(`--${name}:\\s*(#[0-9a-fA-F]{6})\\s*;`));
  assert.ok(match, name);
  return match[1];
}
function luminance(hex) {
  const channels = [1, 3, 5].map((offset) => parseInt(hex.slice(offset, offset + 2), 16) / 255)
    .map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2];
}
function contrast(first, second) {
  const [low, high] = [luminance(first), luminance(second)].sort((a, b) => a - b);
  return (high + .05) / (low + .05);
}
test("selected text palette pairs meet 4.5:1 contrast", () => {
  const pairs = [["text", "surface"], ["muted", "surface"], ["muted", "hero-bg"],
    ["primary-dark", "blue-soft"], ["accent-dark", "teal-soft"], ["surface", "primary-dark"], ["surface", "emergency"]];
  for (const [foreground, background] of pairs) {
    const ratio = contrast(color(foreground), color(background));
    assert.ok(ratio >= 4.5, `${foreground}/${background}: ${ratio}`);
  }
});
test("control borders have at least 3:1 contrast on the page surface", () => {
  assert.ok(contrast(color("control-border"), color("surface")) >= 3);
});
console.log(`${count} shared UI checks passed.`);
