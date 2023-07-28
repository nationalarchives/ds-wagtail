export default function create_dismiss_button(beta_banner) {
    const body = document.querySelector("body");
    const beta_banner_options = document.querySelector(".beta-banner__options");
    const button = document.createElement("button");
    const domain = window.location.hostname;

    button.setAttribute("class", "beta-banner__button");
    button.innerText = "Dismiss this message";
    beta_banner_options.appendChild(button);

    button.addEventListener("click", () => {
        body.removeChild(beta_banner);
        document.cookie = `beta_banner_dismissed=true; domain=${domain}; path=/; Secure`;
    });
}
