import { initAll } from "../../node_modules/@nationalarchives/frontend/nationalarchives/all.mjs";
import { GA4 } from "../../node_modules/@nationalarchives/frontend/nationalarchives/analytics.mjs";

initAll();
new GA4({ addTrackingCode: false });
