export default function extract_usage_policy(cookies) {
    if (cookies) {
        const cookies_array = decodeURIComponent(cookies)
            .split(";")
            .map((index) => index.trim());
        const cookies_policy = cookies_array.filter(
            (index) => index.slice(0, 14) === "cookies_policy"
        )[0];
        const cookies_policy_object = JSON.parse(
            cookies_policy.slice(cookies_policy.indexOf("=") + 1)
        );

        return cookies_policy_object["usage"];
    }

    return false;
}
