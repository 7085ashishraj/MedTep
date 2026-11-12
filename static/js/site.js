"use strict";

(() => {
  // Keep all navigation links visible if JavaScript or Bootstrap is unavailable.
  if (window.bootstrap?.Collapse) document.documentElement.classList.remove("no-js");

  const summary = document.getElementById("form-error-summary");
  if (summary) {
    summary.focus();
    summary.addEventListener("click", (event) => {
      const link = event.target.closest('a[href^="#"]');
      if (!link) return;
      const field = document.getElementById(link.getAttribute("href").slice(1));
      if (!field || field.type === "hidden") return;
      event.preventDefault();
      let details = field.closest("details");
      while (details) {
        details.open = true;
        details = details.parentElement?.closest("details");
      }
      field.focus();
      field.scrollIntoView({ block: "center", behavior: "instant" });
    });
  }

  const menu = document.getElementById("main-navigation");
  const menuButton = document.querySelector('[aria-controls="main-navigation"]');
  if (menu && menuButton && window.bootstrap?.Collapse) {
    const hideMenu = () => window.bootstrap.Collapse.getOrCreateInstance(menu, { toggle: false }).hide();
    menu.addEventListener("keydown", (event) => {
      if (event.key !== "Escape" || !menu.classList.contains("show")) return;
      event.preventDefault();
      hideMenu();
      menuButton.focus();
    });
    document.addEventListener("focusin", (event) => {
      if (menu.classList.contains("show") && !menu.contains(event.target) && !menuButton.contains(event.target)) hideMenu();
    });
  }

  document.querySelectorAll("[data-toggle-password]").forEach((button) => {
    const field = document.getElementById(button.getAttribute("aria-controls"));
    if (!field || field.type !== "password") return;
    button.hidden = false;
    button.addEventListener("click", () => {
      const show = field.type === "password";
      field.type = show ? "text" : "password";
      button.textContent = show ? "Hide" : "Show";
      button.setAttribute("aria-label", `${show ? "Hide" : "Show"} ${button.dataset.passwordLabel.toLowerCase()}`);
    });
  });
})();
