// Isolated browser-API mocks: no live location, phone call or map request is made.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const scripts = path.join(__dirname, "..", "static", "js");
const locationCode = fs.readFileSync(path.join(scripts, "location.js"), "utf8");
const mapCode = fs.readFileSync(path.join(scripts, "facilities.js"), "utf8");
let checks = 0;
function test(name, run) {
  run();
  checks += 1;
  console.log(`PASS ${name}`);
}
function element() {
  return {
    hidden: true, disabled: false, textContent: "", value: "", open: false,
    attributes: {}, events: {}, children: [],
    setAttribute(name, value) { this.attributes[name] = value; },
    addEventListener(name, callback) { this.events[name] = callback; },
    append(...children) { this.children.push(...children); },
  };
}
function locationFixture({ secure = true, available = true } = {}) {
  const button = element(), label = element(), spinner = element(), feedback = element();
  const latitude = element(), longitude = element(), manual = element();
  const nodes = {
    "[data-location-button]": button, "[data-location-label]": label,
    "[data-location-spinner]": spinner, "[data-manual-location]": manual,
  };
  let submissions = 0, calls = 0, success, failure, options;
  const form = {
    querySelector: (key) => nodes[key],
    elements: { namedItem: (name) => name === "latitude" ? latitude : longitude },
    requestSubmit: () => { submissions += 1; },
    addEventListener() {},
  };
  vm.runInNewContext(locationCode, {
    document: { querySelector: () => form, getElementById: () => feedback },
    window: { isSecureContext: secure },
    navigator: available ? { geolocation: {
      getCurrentPosition(ok, fail, config) { calls += 1; success = ok; failure = fail; options = config; },
    } } : {},
  });
  return { button, label, spinner, feedback, latitude, longitude, manual,
    click: () => button.events.click(),
    succeed: (lat, lon) => success({ coords: { latitude: lat, longitude: lon } }),
    fail: (code) => failure({ code }),
    get calls() { return calls; }, get submissions() { return submissions; },
    get options() { return options; },
  };
}

test("location is requested only on a tap, with a finite timeout and no cached fix", () => {
  const state = locationFixture();
  assert.equal(state.calls, 0);
  state.click();
  assert.equal(state.calls, 1);
  assert.equal(state.button.disabled, true);
  assert.equal(state.spinner.hidden, false);
  assert.equal(state.options.timeout, 10000);
  assert.equal(state.options.maximumAge, 0);
});
test("success submits validated rounded coordinates, including zero", () => {
  const state = locationFixture();
  state.click();
  state.succeed(0, 77.59000012);
  assert.equal(state.latitude.value, "0.000000");
  assert.equal(state.longitude.value, "77.590000");
  assert.equal(state.submissions, 1);
  assert.equal(state.button.disabled, false);
});
test("permission denial keeps the page usable and reveals manual entry", () => {
  const state = locationFixture();
  state.click(); state.fail(1);
  assert.match(state.feedback.textContent, /permission was declined/);
  assert.match(state.feedback.textContent, /Search by name or address/);
  assert.equal(state.manual.open, true);
  assert.equal(state.submissions, 0);
  assert.equal(state.button.disabled, false);
});
test("timeouts and unavailable positions stop the spinner", () => {
  for (const code of [2, 3, 99]) {
    const state = locationFixture();
    state.click(); state.fail(code);
    assert.equal(state.spinner.hidden, true);
    assert.equal(state.submissions, 0);
    assert.match(state.feedback.textContent, /demo location/);
  }
});
test("NaN, infinity and out-of-range locations never submit", () => {
  for (const [lat, lon] of [[NaN, 0], [0, Infinity], [91, 0], [0, -181]]) {
    const state = locationFixture();
    state.click(); state.succeed(lat, lon);
    assert.equal(state.submissions, 0);
    assert.match(state.feedback.textContent, /valid location/);
  }
});
test("insecure and unsupported browsers get a fallback without a request", () => {
  for (const options of [{ secure: false }, { available: false }]) {
    const state = locationFixture(options);
    state.click();
    assert.equal(state.calls, 0);
    assert.match(state.feedback.textContent, /Search by name or address/);
  }
});
test("shared location script safely ignores pages without its form", () => {
  vm.runInNewContext(locationCode, { document: { querySelector: () => null } });
});
test("missing Leaflet leaves a helpful list fallback", () => {
  const feedback = element();
  vm.runInNewContext(mapCode, {
    document: { getElementById: (id) => id === "map-feedback" ? feedback : element() }, window: {},
  });
  assert.match(feedback.textContent, /still use every facility card/);
});
test("map popups treat hostile facility text as text, and tile errors preserve the list", () => {
  const feedback = element(), created = [], tileEvents = {};
  const payload = { origin: null, results: [{ id: 1, name: "<img onerror=alert(1)>",
    type_label: "Hospital", latitude: 0, longitude: 0, is_demo: true }] };
  const data = { textContent: JSON.stringify(payload) };
  let popup, markerElement = element(), mapLoaded = false;
  const addCallbacks = [];
  const map = { fitBounds() { mapLoaded = true; addCallbacks.forEach((callback) => callback()); } };
  const L = {
    map: () => map, divIcon: (config) => config,
    tileLayer: () => ({ on(name, callback) { tileEvents[name] = callback; }, addTo() {} }),
    marker: () => ({ addTo() { return this; },
      on(name, callback) { assert.equal(name, "add"); addCallbacks.push(callback); return this; },
      getElement() { assert.equal(mapLoaded, true); return markerElement; },
      bindPopup(node) { popup = node; return this; } }),
  };
  vm.runInNewContext(mapCode, {
    document: {
      getElementById: (id) => id === "map-feedback" ? feedback : id === "facility-map-data" ? data : element(),
      createElement: () => { const node = element(); created.push(node); return node; },
      querySelectorAll: () => [],
    }, window: { L }, L,
  });
  assert.equal(popup.children[0].textContent, payload.results[0].name);
  assert.equal(popup.children[1].textContent, "FAKE sample. Not a real facility.");
  assert.match(markerElement.attributes["aria-label"], /FAKE sample/);
  assert.match(feedback.textContent, /Map ready/);
  tileEvents.tileerror();
  assert.match(feedback.textContent, /facility list are still available/);
});
console.log(`${checks} frontend checks passed.`);
