// This function was written by CoPilot

(function fullUrlPreviewModule() {
  const LAST_SEGMENT_OFFSET = 1;
  const LOOP_INCREMENT = 1;

  const replaceLastSegment = function replaceLastSegment(urlString, slug) {
    try {
      const url = new URL(urlString);
      const segments = url.pathname.split("/").filter(Boolean);

      if (segments.length) {
        segments[segments.length - LAST_SEGMENT_OFFSET] = slug;
      } else {
        segments.push(slug);
      }

      url.pathname = `/${segments.join("/")}/`;
      return url.toString();
    } catch {
      return null;
    }
  };

  const getPreviewUrl = function getPreviewUrl(initialFullUrl, slug) {
    if (!slug) {
      return null;
    }

    if (initialFullUrl) {
      return replaceLastSegment(initialFullUrl, slug);
    }

    return `/${slug}/`;
  };

  const bindContainer = function bindContainer(container) {
    const slugInput = document.getElementById("id_slug");
    const previewRow = container.querySelector(".js-full-url-preview");
    const previewLink = container.querySelector(".js-full-url-preview-link");

    if (!slugInput || !previewRow || !previewLink) {
      return;
    }

    const initialFullUrl = (container.dataset.initialFullUrl || "").trim();

    const updatePreview = function updatePreview() {
      const slug = (slugInput.value || "").trim();
      const previewUrl = getPreviewUrl(initialFullUrl, slug);

      if (!previewUrl) {
        previewRow.hidden = true;
        previewLink.removeAttribute("href");
        previewLink.textContent = "";
        return;
      }

      previewRow.hidden = false;
      previewLink.textContent = previewUrl;
      previewLink.setAttribute("href", previewUrl);
    };

    slugInput.addEventListener("input", updatePreview);
    slugInput.addEventListener("change", updatePreview);
    updatePreview();
  };

  const init = function init() {
    const containers = document.querySelectorAll(".js-full-url-help");

    for (let index = 0; index < containers.length; index += LOOP_INCREMENT) {
      bindContainer(containers[index]);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
