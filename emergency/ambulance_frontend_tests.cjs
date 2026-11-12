// Browser API mocks only: no real transport, GPS or network request.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const code = fs.readFileSync(path.join(__dirname, "..", "static", "js", "ambulance.js"), "utf8");
const statuses = ["requested", "accepted", "on_the_way", "completed"];
const settle = () => new Promise(setImmediate);

function node() {
  const element = { textContent: "", hidden: false, attributes: {}, classes: new Map(),
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
  };
  element.classList = { toggle: (name, value) => element.classes.set(name, value) };
  Object.defineProperty(element, "innerHTML", { set() { throw Error("Unsafe HTML insertion"); } });
  return element;
}
function snapshot(status = "accepted") {
  const current = statuses.indexOf(status);
  return { status, status_label: status === "accepted" ? "Accepted" : "Completed", facility: null,
    timeline: statuses.map((value, index) => ({ status: value, is_reached: index <= current,
      is_current: index === current, recorded_at: index <= current ? "2026-11-12T12:00:00Z" : null })) };
}
function fixture({ initial = "requested", hidden = false, response } = {}) {
  const elements = {};
  for (const id of ["ambulance-poll-feedback", "ambulance-current-status", "ambulance-facility-name", "ambulance-facility-demo"]) elements[id] = node();
  elements["ambulance-current-status"].textContent = "Requested";
  const steps = statuses.map((status) => {
    const element = node(); element.dataset = { ambulanceStep: status };
    element.time = node(); element.querySelector = () => element.time;
    return element;
  });
  const root = { dataset: { status: initial, statusUrl: "/emergency/ambulance/1/status/" }, querySelectorAll: () => steps };
  const timers = new Map(), events = {}, calls = [];
  let timerId = 0;
  const document = { visibilityState: hidden ? "hidden" : "visible",
    getElementById: (id) => id === "ambulance-progress" ? root : elements[id],
    addEventListener: (name, callback) => { events[name] = callback; },
  };
  vm.runInNewContext(code, {
    document, Intl, Date, AbortController,
    setTimeout: (callback, delay) => { timerId += 1; timers.set(timerId, { callback, delay }); return timerId; },
    clearTimeout: (id) => timers.delete(id),
    fetch: async (url, options) => {
      calls.push({ url, options });
      if (response instanceof Error) throw response;
      return response || { ok: true, redirected: false, json: async () => snapshot() };
    },
  });
  return { elements, steps, root, timers, document, calls,
    async tick() {
      const [id, timer] = [...timers][0]; timers.delete(id); await timer.callback();
    },
    async show() { document.visibilityState = "visible"; events.visibilitychange(); await settle(); },
  };
}

(async () => {
  let count = 0;
  async function test(name, run) { await run(); count += 1; console.log(`PASS ${name}`); }
  await test("polling waits ten seconds and only performs an authenticated read", async () => {
    const state = fixture();
    assert.equal(state.calls.length, 0);
    assert.equal([...state.timers.values()][0].delay, 10000);
    await state.tick();
    assert.equal(state.calls.length, 1);
    assert.equal(state.calls[0].options.credentials, "same-origin");
    assert.equal(state.calls[0].options.cache, "no-store");
    assert.equal(state.calls[0].options.method, undefined);
  });
  await test("an update changes status and recorded timeline accessibly", async () => {
    const state = fixture(); await state.tick();
    assert.equal(state.elements["ambulance-current-status"].textContent, "Accepted");
    assert.equal(state.steps[1].attributes["aria-current"], "step");
    assert.equal(state.steps[2].time.textContent, "Waiting for an operator update");
    assert.match(state.steps[1].time.textContent, /IST/);
  });
  await test("hidden tabs do not poll and resume when visible", async () => {
    const state = fixture({ hidden: true });
    assert.equal(state.timers.size, 0);
    assert.equal(state.calls.length, 0);
    await state.show();
    assert.equal(state.calls.length, 1);
  });
  await test("completed initial requests never poll", () => {
    const state = fixture({ initial: "completed" });
    assert.equal(state.timers.size, 0);
    assert.equal(state.calls.length, 0);
  });
  await test("a received completion stops subsequent checks", async () => {
    const state = fixture({ response: { ok: true, json: async () => snapshot("completed") } });
    await state.tick();
    assert.equal(state.timers.size, 0);
    assert.match(state.elements["ambulance-poll-feedback"].textContent, /checks are stopped/);
  });
  await test("network failures and expired sessions preserve the last status with a refresh fallback", async () => {
    for (const response of [new Error("offline"), { ok: false }, { ok: true, redirected: true }]) {
      const state = fixture({ response }); await state.tick();
      assert.equal(state.elements["ambulance-current-status"].textContent, "Requested");
      assert.match(state.elements["ambulance-poll-feedback"].textContent, /out of date/);
      assert.equal(state.timers.size, 0);
    }
  });
  await test("facility names are inserted as text and demo flags stay visible", async () => {
    const data = snapshot(); data.facility = { name: "<img onerror=alert(1)>", is_demo: true };
    const state = fixture({ response: { ok: true, json: async () => data } });
    await state.tick();
    assert.equal(state.elements["ambulance-facility-name"].textContent, data.facility.name);
    assert.equal(state.elements["ambulance-facility-demo"].hidden, false);
  });
  await test("invalid status payload pauses rather than implying progress", async () => {
    const state = fixture({ response: { ok: true, json: async () => ({ status: "dispatched", timeline: [] }) } });
    await state.tick();
    assert.equal(state.elements["ambulance-current-status"].textContent, "Requested");
    assert.equal(state.timers.size, 0);
  });
  console.log(`${count} ambulance frontend checks passed.`);
})().catch((error) => { console.error(error); process.exitCode = 1; });
