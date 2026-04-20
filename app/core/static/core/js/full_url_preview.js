// This function was written by CoPilot

(function () {
  "use strict";

  function replaceLastSegment(urlString, slug) {
    try {
      var url = new URL(urlString);
      var segments = url.pathname.split("/").filter(Boolean);

      if (segments.length) {
        segments[segments.length - 1] = slug;
      } else {
        segments.push(slug);
      }

      url.pathname = "/" + segments.join("/") + "/";
      return url.toString();
    } catch (error) {
      return null;
    }
  }

  function getPreviewUrl(initialFullUrl, slug) {
    if (!slug) {
      return null;
    }

    if (initialFullUrl) {
      return replaceLastSegment(initialFullUrl, slug);
    }

    return "/" + slug + "/";
  }

  function bindContainer(container) {
    var slugInput = document.getElementById("id_slug");
    var previewRow = container.querySelector(".js-full-url-preview");
    var previewLink = container.querySelector(".js-full-url-preview-link");

    if (!slugInput || !previewRow || !previewLink) {
      return;
    }

    var initialFullUrl = (container.dataset.initialFullUrl || "").trim();

    function updatePreview() {
      var slug = (slugInput.value || "").trim();
      var previewUrl = getPreviewUrl(initialFullUrl, slug);

      if (!previewUrl) {
        previewRow.hidden = true;
        previewLink.removeAttribute("href");
        previewLink.textContent = "";
        return;
      }

      previewRow.hidden = false;
      previewLink.textContent = previewUrl;
      previewLink.setAttribute("href", previewUrl);
    }

    slugInput.addEventListener("input", updatePreview);
    slugInput.addEventListener("change", updatePreview);
    updatePreview();
  }

  function init() {
    var containers = document.querySelectorAll(".js-full-url-help");

    for (var i = 0; i < containers.length; i += 1) {
      bindContainer(containers[i]);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
