// Run with Node. Mocks never request real GPS, contact anybody, or send an SMS.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const code = fs.readFileSync(path.join(__dirname, "..", "static", "js", "sos.js"), "utf8");
const uuid = "00000000-0000-4000-8000-000000000001";
const detail = `/emergency/sos/${uuid}/`;
const settle = () => new Promise(setImmediate);

function element() {
  return { hidden: true, value: "message & location", textContent: "", attributes: {}, events: {},
    addEventListener(name, callback) { this.events[name] = callback; },
    setAttribute(name, value) { this.attributes[name] = value; },
    focus() { this.focused = true; }, select() { this.selected = true; },
  };
}
function fixture({ guest = false, secure = true, fetchImpl, clipboardFails = false } = {}) {
  const nodes = {};
  for (const id of ["sos-request-form", "sos-feedback", "sos-feedback-text", "sos-spinner", "sos-fallback", "sos-feedback-dismiss", "copy-sos-message", "sos-message", "copy-feedback"]) nodes[id] = element();
  nodes["sos-request-form"].action = "/emergency/sos/create/";
  const triggers = [element(), element()];
  const captures = [], posts = [], navigations = [], copies = [];
  let idCalls = 0;
  class FakeFormData {
    constructor() { this.values = new Map([["csrfmiddlewaretoken", "isolated-test-token"]]); }
    set(key, value) { this.values.set(key, value); }
    get(key) { return this.values.get(key); }
  }
  vm.runInNewContext(code, {
    document: { getElementById: (id) => guest && id === "sos-request-form" ? null : nodes[id], querySelectorAll: () => triggers },
    window: { isSecureContext: secure, crypto: { randomUUID: () => { idCalls += 1; return uuid; } }, location: { assign: (url) => navigations.push(url) } },
    navigator: { geolocation: { getCurrentPosition: (ok, fail, options) => captures.push({ ok, fail, options }) },
      clipboard: { async writeText(text) { if (clipboardFails) throw Error("denied"); copies.push(text); } } },
    FormData: FakeFormData, AbortController, setTimeout, clearTimeout,
    fetch: async (url, options) => {
      posts.push({ url, options });
      if (fetchImpl) return fetchImpl();
      return { ok: true, redirected: false, json: async () => ({ url: detail, created: true }) };
    },
  });
  return { nodes, triggers, captures, posts, navigations, copies,
    click: (index = 0, event = {}) => triggers[index].events.click({ preventDefault() {}, ...event }),
    success: (lat = 0, lon = 77.59000012) => captures.at(-1).ok({ coords: { latitude: lat, longitude: lon } }),
    get idCalls() { return idCalls; },
  };
}

(async () => {
  let count = 0;
  async function test(name, run) { await run(); count += 1; console.log(`PASS ${name}`); }
  await test("guest links keep their normal login destination", () => {
    const state = fixture({ guest: true });
    assert.equal(state.triggers[0].events.click, undefined);
    assert.equal(state.captures.length, 0);
  });
  await test("capture starts on a tap only and duplicate desktop/mobile taps are ignored", () => {
    const state = fixture();
    assert.equal(state.captures.length, 0);
    state.click(0); state.click(1);
    assert.equal(state.captures.length, 1);
    assert.equal(state.captures[0].options.timeout, 10000);
    assert.equal(state.captures[0].options.maximumAge, 0);
    assert.equal(state.nodes["sos-spinner"].hidden, false);
    assert.equal(state.triggers[1].attributes["aria-disabled"], "true");
  });
  await test("a successful capture includes CSRF, rounds coordinates and navigates to the owned result", async () => {
    const state = fixture(); state.click(); state.success(); await settle();
    assert.equal(state.posts.length, 1);
    const options = state.posts[0].options;
    assert.equal(options.method, "POST");
    assert.equal(options.body.get("csrfmiddlewaretoken"), "isolated-test-token");
    assert.equal(options.body.get("latitude"), "0.000000");
    assert.equal(options.body.get("longitude"), "77.590000");
    assert.equal(options.body.get("request_id"), uuid);
    assert.deepEqual(state.navigations, [detail]);
  });
  await test("denial, unavailability and timeout reveal the manual fallback without posting", () => {
    for (const errorCode of [1, 2, 3, 99]) {
      const state = fixture(); state.click(); state.captures[0].fail({ code: errorCode });
      assert.equal(state.posts.length, 0);
      assert.equal(state.nodes["sos-spinner"].hidden, true);
      assert.equal(state.nodes["sos-fallback"].hidden, false);
      assert.match(state.nodes["sos-feedback-text"].textContent, /manual entry/);
    }
  });
  await test("nonfinite and out-of-range fixes never reach the server", () => {
    for (const [lat, lon] of [[NaN, 0], [0, Infinity], [91, 0], [0, -181]]) {
      const state = fixture(); state.click(); state.success(lat, lon);
      assert.equal(state.posts.length, 0);
      assert.match(state.nodes["sos-feedback-text"].textContent, /valid coordinates/);
    }
  });
  await test("an uncertain network save keeps the UUID for a safe retry", async () => {
    let attempt = 0;
    const state = fixture({ fetchImpl: () => {
      attempt += 1;
      if (attempt === 1) throw Error("offline");
      return { ok: true, redirected: false, json: async () => ({ url: detail }) };
    } });
    state.click(); state.success(); await settle();
    assert.match(state.nodes["sos-feedback-text"].textContent, /couldn't confirm/);
    state.click(); state.success(); await settle();
    assert.equal(state.posts.length, 2);
    assert.equal(state.posts[0].options.body.get("request_id"), state.posts[1].options.body.get("request_id"));
    assert.equal(state.idCalls, 1);
    assert.deepEqual(state.navigations, [detail]);
  });
  await test("expired login and non-success responses never pretend a save succeeded", async () => {
    for (const response of [{ ok: false }, { ok: true, redirected: true }]) {
      const state = fixture({ fetchImpl: () => response });
      state.click(); state.success(); await settle();
      assert.equal(state.navigations.length, 0);
      assert.match(state.nodes["sos-feedback-text"].textContent, /Recently saved/);
    }
  });
  await test("untrusted redirect URLs cannot navigate away", async () => {
    const state = fixture({ fetchImpl: () => ({ ok: true, json: async () => ({ url: "https://example.invalid/" }) }) });
    state.click(); state.success(); await settle();
    assert.equal(state.navigations.length, 0);
  });
  await test("insecure contexts and modified clicks do not capture GPS", () => {
    const state = fixture({ secure: false }); state.click();
    assert.equal(state.captures.length, 0);
    assert.match(state.nodes["sos-feedback-text"].textContent, /Automatic location capture is unavailable/);
    const modified = fixture(); modified.click(0, { ctrlKey: true });
    assert.equal(modified.captures.length, 0);
  });
  await test("copying only writes the message to the clipboard", async () => {
    const state = fixture(); await state.nodes["copy-sos-message"].events.click();
    assert.deepEqual(state.copies, [state.nodes["sos-message"].value]);
    assert.equal(state.posts.length, 0);
    assert.match(state.nodes["copy-feedback"].textContent, /send it yourself/);
  });
  await test("clipboard denial selects the message and explains manual copy", async () => {
    const state = fixture({ clipboardFails: true }); await state.nodes["copy-sos-message"].events.click();
    assert.equal(state.nodes["sos-message"].selected, true);
    assert.match(state.nodes["copy-feedback"].textContent, /Copy command/);
  });
  await test("hiding a failed SOS notice returns focus without sending or changing the retry ID", () => {
    const state = fixture(); state.click(1);
    assert.equal(state.nodes["sos-feedback-dismiss"].hidden, true);
    state.captures[0].fail({ code: 1 });
    assert.equal(state.nodes["sos-feedback-dismiss"].hidden, false);
    state.nodes["sos-feedback-dismiss"].events.click();
    assert.equal(state.nodes["sos-feedback"].hidden, true);
    assert.equal(state.triggers[1].focused, true);
    assert.equal(state.posts.length, 0);
    state.click(1);
    assert.equal(state.idCalls, 1);
  });
  console.log(`${count} SOS frontend checks passed.`);
})().catch((error) => { console.error(error); process.exitCode = 1; });
