"use strict";

(() => {
  const form = document.getElementById("sos-request-form");
  if (form) {
    const triggers = document.querySelectorAll("[data-sos-trigger]");
    const feedback = document.getElementById("sos-feedback");
    const text = document.getElementById("sos-feedback-text");
    const spinner = document.getElementById("sos-spinner");
    const fallback = document.getElementById("sos-fallback");
    const dismiss = document.getElementById("sos-feedback-dismiss");
    let busy = false;
    let requestId = null;
    let originTrigger = null;

    function show(message, loading = false) {
      feedback.hidden = false;
      spinner.hidden = !loading;
      text.textContent = message;
      fallback.hidden = loading;
      if (dismiss) dismiss.hidden = loading;
      triggers.forEach((trigger) => trigger.setAttribute("aria-disabled", String(loading)));
      feedback.focus();
    }

    function fail(message) {
      busy = false;
      show(message);
    }

    if (dismiss) dismiss.addEventListener("click", () => {
      // Hiding a failure notice does not cancel, delete or resend a request.
      feedback.hidden = true;
      originTrigger?.focus();
    });

    async function save(latitude, longitude) {
      const body = new FormData(form);
      body.set("request_id", requestId);
      body.set("latitude", latitude.toFixed(6));
      body.set("longitude", longitude.toFixed(6));
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 15000);
      show("Saving your location. No one is being contacted automatically.", true);
      try {
        const response = await fetch(form.action, {
          method: "POST", body, credentials: "same-origin",
          headers: { Accept: "application/json" }, signal: controller.signal,
        });
        if (!response.ok || response.redirected) throw new Error("Save unconfirmed");
        const data = await response.json();
        if (typeof data.url !== "string" || !/^\/emergency\/sos\/[0-9a-f-]+\/$/i.test(data.url)) {
          throw new Error("Invalid redirect");
        }
        window.location.assign(data.url);
      } catch {
        fail("We couldn't confirm saving. Check Recently saved on the SOS page, or tap SOS to retry. Retrying this button uses the same request ID.");
      } finally {
        clearTimeout(timer);
      }
    }

    triggers.forEach((trigger) => trigger.addEventListener("click", (event) => {
      // Preserve ordinary open-in-new-tab behavior; GET never creates a request.
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      if (busy) return;
      originTrigger = trigger;
      if (!window.isSecureContext || !navigator.geolocation || !window.crypto?.randomUUID) {
        fail("Automatic location capture is unavailable. Use the SOS page to enter coordinates, or call 112.");
        return;
      }
      busy = true;
      requestId = requestId || window.crypto.randomUUID();
      show("Finding your location. Your browser may ask for permission. For urgent help, call 112.", true);
      try {
        navigator.geolocation.getCurrentPosition((position) => {
          const { latitude, longitude } = position.coords;
          if (!Number.isFinite(latitude) || !Number.isFinite(longitude) ||
              Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
            fail("We couldn't read valid coordinates. Open the SOS page for manual entry or call 112.");
            return;
          }
          save(latitude, longitude);
        }, (error) => {
          const errors = {
            1: "Location permission was declined.",
            2: "Your location is unavailable right now.",
            3: "Finding your location took too long.",
          };
          fail((errors[error.code] || "Location capture failed.") + " Open the SOS page for manual entry, or call 112.");
        }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
      } catch {
        fail("Location capture failed. Open the SOS page for manual entry, or call 112.");
      }
    }));
  }

  const copyButton = document.getElementById("copy-sos-message");
  const message = document.getElementById("sos-message");
  const copyFeedback = document.getElementById("copy-feedback");
  if (copyButton && message) {
    copyButton.hidden = false;
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(message.value);
        copyFeedback.textContent = "Message copied. Paste it into your chosen app and send it yourself.";
      } catch {
        message.focus();
        message.select();
        copyFeedback.textContent = "Copy is unavailable. The message is selected; use your device's Copy command.";
      }
    });
  }
})();
