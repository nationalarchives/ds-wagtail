(() => {
  const initTreeExplorer = () => {
    const treeRoot = document.querySelector(".tree-explorer__list");
    if (!treeRoot) {
      return;
    }

    const expandButton = document.querySelector(
      '[data-tree-action="expand-all"]',
    );
    const collapseButton = document.querySelector(
      '[data-tree-action="collapse-all"]',
    );

    const setAll = (expanded) => {
      treeRoot.querySelectorAll(".tree-node__details").forEach((details) => {
        details.open = expanded;
      });
    };

    if (expandButton) {
      expandButton.addEventListener("click", () => setAll(true));
    }

    if (collapseButton) {
      collapseButton.addEventListener("click", () => setAll(false));
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTreeExplorer);
    return;
  }

  initTreeExplorer();
})();
