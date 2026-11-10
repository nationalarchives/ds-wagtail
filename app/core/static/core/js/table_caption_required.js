// JS produced by Copilot

{
  const CAPTION_LABEL_SELECTOR =
    'label.w-field__label[for$="-handsontable-col-caption"]';
  const LOOP_INCREMENT = 1;
  const REQUIRED_MARK_CLASS = "w-required-mark";

  const getCaptionInput = function getCaptionInput(label) {
    const inputId = label.getAttribute("for");

    if (!inputId) {
      return null;
    }

    return document.getElementById(inputId);
  };

  const setInputRequired = function setInputRequired(input) {
    if (input) {
      input.required = true;
      input.setAttribute("aria-required", "true");
    }
  };

  const addRequiredMark = function addRequiredMark(label) {
    if (label.querySelector(`.${REQUIRED_MARK_CLASS}`)) {
      return;
    }

    const requiredMark = document.createElement("span");
    requiredMark.className = REQUIRED_MARK_CLASS;
    requiredMark.textContent = "*";
    label.appendChild(requiredMark);
  };

  const decorateLabel = function decorateLabel(label) {
    setInputRequired(getCaptionInput(label));
    addRequiredMark(label);
  };

  const decorateLabels = function decorateLabels(root) {
    if (!root.querySelectorAll) {
      return;
    }

    if (root.matches && root.matches(CAPTION_LABEL_SELECTOR)) {
      decorateLabel(root);
    }

    const labels = root.querySelectorAll(CAPTION_LABEL_SELECTOR);

    for (let index = 0; index < labels.length; index += LOOP_INCREMENT) {
      decorateLabel(labels[index]);
    }
  };

  const init = function init() {
    decorateLabels(document);

    const observer = new MutationObserver((mutations) => {
      for (let index = 0; index < mutations.length; index += LOOP_INCREMENT) {
        const mutation = mutations[index];

        for (
          let childIndex = 0;
          childIndex < mutation.addedNodes.length;
          childIndex += LOOP_INCREMENT
        ) {
          decorateLabels(mutation.addedNodes[childIndex]);
        }
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
}
