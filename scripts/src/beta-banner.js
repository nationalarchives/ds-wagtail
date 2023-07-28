import create_dismiss_button from "./modules/beta_banner/create_dismiss_button";
import extract_usage_policy from "./modules/beta_banner/extract_usage_policy";

document.addEventListener("DOMContentLoaded", () => {
    const accept_cookies_button = document.querySelector(
        "#accept_optional_cookies",
    );
    const beta_banner = document.querySelector(".beta-banner");
    const cookies_usage_policy = extract_usage_policy(document.cookie);

    if (beta_banner && accept_cookies_button) {
        accept_cookies_button.addEventListener("click", () => {
            create_dismiss_button(beta_banner);
        });
    } else if (beta_banner && cookies_usage_policy) {
        create_dismiss_button(beta_banner);
    }
});
