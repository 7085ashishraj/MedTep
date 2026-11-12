"use strict";

(() => {
  const root = document.getElementById("ambulance-progress");
  if (!root) return;
  const feedback = document.getElementById("ambulance-poll-feedback");
  const steps = [...root.querySelectorAll("[data-ambulance-step]")];
  let stopped = root.dataset.status === "completed";
  let busy = false;
  let timer;
  const dateFormat = new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Kolkata",
  });

  function schedule() {
    if (!stopped && document.visibilityState !== "hidden") timer = setTimeout(refresh, 10000);
  }

  async function refresh() {
    if (stopped || busy || document.visibilityState === "hidden") return;
    busy = true;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(root.dataset.statusUrl, {
        credentials: "same-origin", cache: "no-store", headers: { Accept: "application/json" },
        signal: controller.signal,
      });
      if (!response.ok || response.redirected) throw new Error("Status unavailable");
      const data = await response.json();
      if (!steps.some((step) => step.dataset.ambulanceStep === data.status) || !Array.isArray(data.timeline)) {
        throw new Error("Invalid progress response");
      }
      document.getElementById("ambulance-current-status").textContent = data.status_label;
      for (const element of steps) {
        const step = data.timeline.find((item) => item.status === element.dataset.ambulanceStep);
        if (!step) throw new Error("Missing progress step");
        element.classList.toggle("ambulance-step-reached", step.is_reached);
        element.classList.toggle("ambulance-step-current", step.is_current);
        if (step.is_current) element.setAttribute("aria-current", "step");
        else element.removeAttribute("aria-current");
        element.querySelector("[data-step-time]").textContent = step.recorded_at
          ? dateFormat.format(new Date(step.recorded_at)) + " IST"
          : step.is_reached ? "Timestamp not recorded" : "Waiting for an operator update";
      }
      document.getElementById("ambulance-facility-name").textContent = data.facility
        ? data.facility.name : "No reference facility selected";
      document.getElementById("ambulance-facility-demo").hidden = !data.facility?.is_demo;
      root.dataset.status = data.status;
      stopped = data.status === "completed";
      feedback.textContent = stopped
        ? "Project workflow completed. Automatic checks are stopped."
        : "Latest operator-reported project status loaded. Checks every 10 seconds while this page is visible.";
    } catch {
      stopped = true;
      feedback.textContent = "Automatic updates are paused. Use Refresh status to reconnect or sign in again. The last displayed status may be out of date.";
    } finally {
      clearTimeout(timeout);
      busy = false;
      schedule();
    }
  }

  document.addEventListener("visibilitychange", () => {
    clearTimeout(timer);
    if (!stopped && document.visibilityState !== "hidden") refresh();
  });
  if (!stopped) feedback.textContent = "Checking operator-reported project status every 10 seconds while this page is visible.";
  schedule();
})();
