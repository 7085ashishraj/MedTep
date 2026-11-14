"use strict";

(() => {
  const element = document.getElementById("facility-map");
  const dataElement = document.getElementById("facility-map-data");
  const feedback = document.getElementById("map-feedback");
  if (!element || !dataElement) return;
  if (!window.L) {
    feedback.textContent = "The map couldn't load. You can still use every facility card.";
    return;
  }

  try {
    const data = JSON.parse(dataElement.textContent);
    const map = L.map(element, { scrollWheelZoom: false });
    const points = [];
    const markers = new Map();
    // OSM attribution remains visible; normal browser caching is preserved.
    const tiles = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    });
    tiles.on("tileerror", () => {
      feedback.textContent = "Some map tiles couldn't load. Pins and the facility list are still available.";
    });
    tiles.addTo(map);

    data.results.forEach((facility, index) => {
      const point = [facility.latitude, facility.longitude];
      points.push(point);
      const marker = L.marker(point, {
        title: facility.name,
        alt: `${index + 1}. ${facility.name}${facility.is_demo ? " — FAKE sample" : ""}`,
        icon: L.divIcon({
          className: `facility-pin${facility.is_demo ? " facility-pin-demo" : ""}`,
          html: `<span>${index + 1}</span>${facility.is_demo ? '<small>Demo</small>' : ""}`,
          iconSize: [48, 48], iconAnchor: [24, 48], popupAnchor: [0, -48],
        }),
      });
      // Leaflet creates the marker DOM only after the map has a view.
      marker.on("add", () => {
        marker.getElement().setAttribute("aria-label", `${index + 1}. ${facility.name}${facility.is_demo ? " — FAKE sample" : ""}`);
      }).addTo(map);
      const popup = document.createElement("div");
      const title = document.createElement("strong");
      title.textContent = facility.name;
      const description = document.createElement("p");
      description.textContent = facility.is_demo ? "FAKE sample. Not a real facility." : facility.type_label;
      const link = document.createElement("a");
      link.href = `#facility-${facility.id}`;
      link.textContent = "View facility card";
      link.className = "map-card-link";
      link.addEventListener("click", () => {
        document.getElementById(`facility-${facility.id}`).focus();
      });
      popup.append(title, description, link);
      marker.bindPopup(popup);
      markers.set(String(facility.id), marker);
    });

    if (data.origin) {
      const origin = [data.origin.latitude, data.origin.longitude];
      points.push(origin);
      const originMarker = L.marker(origin, {
        title: "Search location", alt: "Search location",
        icon: L.divIcon({ className: "search-location-pin", html: "<span>◎</span>", iconSize: [44, 44] }),
      });
      originMarker.on("add", () => {
        originMarker.getElement().setAttribute("aria-label", "Search location");
      }).addTo(map).bindPopup("Search location (the coordinates you supplied)");
    }
    if (points.length) map.fitBounds(points, { padding: [32, 32], maxZoom: 14 });
    else map.setView([22.5, 79], 4);
    const searchArea = document.getElementById("map-area-search");
    if (searchArea) {
      searchArea.hidden = false;
      searchArea.addEventListener("click", () => {
        const centre = map.getCenter();
        const form = document.querySelector("[data-location-form]");
        if (!form || !Number.isFinite(centre.lat) || !Number.isFinite(centre.lng)) return;
        form.elements.namedItem("latitude").value = Math.max(-90, Math.min(90, centre.lat)).toFixed(6);
        // Leaflet can wrap the world; normalise its longitude to the accepted range.
        form.elements.namedItem("longitude").value = (((centre.lng + 180) % 360 + 360) % 360 - 180).toFixed(6);
        const manual = form.querySelector("[data-manual-location]");
        if (manual) manual.open = true;
        form.requestSubmit();
      });
    }
    feedback.textContent = data.results.length
      ? "Map ready. Select a numbered pin to see its facility."
      : !data.origin ? "Choose a search location to find nearby facilities."
        : data.search?.status === "unavailable" ? "Directory lookup unavailable. Please retry shortly; this does not mean there are no facilities nearby."
          : "No mapped facilities match this search. Try widening your filters; map coverage may be incomplete.";

    document.querySelectorAll("[data-show-on-map]").forEach((button) => {
      const marker = markers.get(button.dataset.showOnMap);
      if (!marker) return;
      button.hidden = false;
      button.addEventListener("click", () => {
        map.setView(marker.getLatLng(), 15);
        marker.openPopup();
        element.scrollIntoView({ block: "center", behavior: "auto" });
        marker.getElement().focus();
      });
    });
  } catch {
    feedback.textContent = "The map is unavailable right now. Please use the facility list.";
  }
})();
