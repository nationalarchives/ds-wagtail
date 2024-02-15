import React from "react";
import { createRoot } from "react-dom/client";
import Clover from "./Clover.js";

const root = createRoot(document.getElementById("clover-viewer"));
root.render(<Clover />);
