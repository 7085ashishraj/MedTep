"use strict";

(() => {
  const form = document.querySelector("[data-location-form]");
  if (!form) return;
  const button = form.querySelector("[data-location-button]");
  const label = form.querySelector("[data-location-label]");
  const spinner = form.querySelector("[data-location-spinner]");
  const feedback = document.getElementById("location-feedback");
  const latitudeInput = form.elements.namedItem("latitude");
  const longitudeInput = form.elements.namedItem("longitude");
  const manual = form.querySelector("[data-manual-location]");
  if (!button || !latitudeInput || !longitudeInput) return;

  function setLoading(loading) {
    button.disabled = loading;
    button.setAttribute("aria-busy", String(loading));
    spinner.hidden = !loading;
    label.textContent = loading ? "Finding location…" : "Use my location";
  }

  function failure(message) {
    setLoading(false);
    feedback.textContent = message + " Enter coordinates from your map app to choose a search area. Name and address filter listings in that area.";
    if (manual) manual.open = true;
  }

  button.addEventListener("click", () => {
    if (!window.isSecureContext) {
      failure("Location needs HTTPS (or localhost during development).");
      return;
    }
    if (!navigator.geolocation) {
      failure("Your browser cannot share a location.");
      return;
    }
    setLoading(true);
    feedback.textContent = "Finding your location. Your browser may ask for permission.";
    try {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords;
        if (!Number.isFinite(latitude) || !Number.isFinite(longitude) ||
            Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
          failure("We couldn't read a valid location.");
          return;
        }
        latitudeInput.value = latitude.toFixed(6);
        longitudeInput.value = longitude.toFixed(6);
        // Prevent a bad field in closed <details> from being unfocusable.
        if (manual) manual.open = true;
        setLoading(false);
        feedback.textContent = "Location received. Finding nearby facilities…";
        form.requestSubmit();
      }, (error) => {
        const messages = {
          1: "Location permission was declined. That's okay.",
          2: "Your location is unavailable right now.",
          3: "Finding your location took too long. You can try again.",
        };
        failure(messages[error.code] || "We couldn't get your location.");
      }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 });
    } catch {
      failure("We couldn't get your location.");
    }
  });
  form.addEventListener("invalid", () => {
    if (manual) manual.open = true;
  }, true);
  form.addEventListener("submit", () => {
    setLoading(true);
    label.textContent = "Searching nearby…";
    feedback.textContent = "Searching healthcare listings. A new area can take a few seconds. Call 112 directly for urgent help.";
  });
  window.addEventListener("pageshow", (event) => {
    // Back/forward cache can restore the old page with its submitting state.
    if (!event.persisted) return;
    setLoading(false);
    feedback.textContent = "Choose a search area or update the filters when you're ready.";
  });
})();
