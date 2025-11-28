const lengthIndicatorClassname = "inputlengthindicator";
const lengthIndicatorExceededClassname = "inputlengthindicator--exceeded";
const countHTMLBase = '<span class="w-sr-only">Character count:</span> ';

const countChars = (text) => {
  /*
  Count characters in a string, with special processing to account for astral symbols in UCS-2. See:
  - https://github.com/RadLikeWhoa/Countable/blob/master/Countable.js#L29
  - https://mathiasbynens.be/notes/javascript-unicode
  - https://github.com/tc39/proposal-intl-segmenter
  */
  if (text) {
    // Find as many matches as there are (g), matching newlines as characters (s), as unicode code points (u).
    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions#advanced_searching_with_flags.
    const matches = text.match(/./gsu);
    return matches ? matches.length : 0;
  }
  return 0;
};

const updateLengthIndicator = (lengthIndicator, length, maxChars) => {
  lengthIndicator.innerHTML = countHTMLBase + `${length}/${maxChars}`;

  if (length > maxChars) {
    lengthIndicator.classList.add(lengthIndicatorExceededClassname);
  } else {
    lengthIndicator.classList.remove(lengthIndicatorExceededClassname);
  }
};

const initializeLengthIndicator = (input) => {
  // Look for relevant attributes on the input
  const maxChars = input.getAttribute("maxlength");

  // Add hidden HTML element to display the count
  const lengthIndicator = document.createElement("div");
  lengthIndicator.classList.add(lengthIndicatorClassname, "w-help-text");
  lengthIndicator.style.visibility = "hidden";
  input.after(lengthIndicator);

  // Add initial value to indicator
  const charCount = countChars(input.value);
  updateLengthIndicator(lengthIndicator, charCount, maxChars);

  input.onfocus = function () {
    lengthIndicator.style.visibility = "visible";
  };

  input.onblur = function () {
    lengthIndicator.style.visibility = "hidden";
  };

  input.oninput = function () {
    // Update indicator to reflect changes
    const charCount = countChars(input.value);
    updateLengthIndicator(lengthIndicator, charCount, maxChars);
  };
};

document.addEventListener("DOMContentLoaded", function () {
  for (let input of document.querySelectorAll(
    ".w-field__input input[maxlength], .w-field__input textarea[maxlength]",
  )) {
    initializeLengthIndicator(input);
  }
});
