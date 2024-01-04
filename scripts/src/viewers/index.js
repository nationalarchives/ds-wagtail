import React from "react";
import { createRoot } from 'react-dom/client';
import Clover from './Clover.js';
import UniversalViewer from "./universal-viewer.js";

const root = createRoot(document.getElementById('clover-viewer'));
root.render(<Clover />);

document.addEventListener("DOMContentLoaded", () => {
    for (const uv of document.querySelectorAll("[data-uv]")) {
        new UniversalViewer(uv);
    }
});
