import Mirador from "mirador/dist/es/src/index";
import { miradorImageToolsPlugin } from "mirador-image-tools";

const viewer = document.getElementById("mirador-viewer");
const manifestID = viewer.getAttribute("data-id");

const config = {
  id: "mirador-viewer",
  windows: [
    {
      imageToolsEnabled: true,
      imageToolsOpen: true,
      manifestId: manifestID,
    },
  ],
  theme: {
    palette: {
      primary: {
        main: "#1967d2",
      },
    },
  },
};

Mirador.viewer(config, [...miradorImageToolsPlugin]);