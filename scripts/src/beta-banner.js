document.addEventListener("DOMContentLoaded", () => {
    const body = document.querySelector("body");
    const beta_banner = document.querySelector(".beta-banner");

    if(beta_banner) {
        const beta_banner_options = document.querySelector(".beta-banner__options");
        const button = document.createElement("button");

        button.setAttribute("class", "beta-banner__button");
        button.innerText = "Dismiss this message";
        beta_banner_options.appendChild(button);

        button.addEventListener("click", () => {
            body.removeChild(beta_banner);
            document.cookie = "beta_banner_dismissed=true";
        })
    }
});