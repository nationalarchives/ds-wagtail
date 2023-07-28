import calc_scroll_percent_increment from "./calc_scroll_percent_increment";

const get_scroll_percentage = () => {
    if (sessionStorage.getItem(window.location.href)) {
        return sessionStorage.getItem(window.location.href);
    } else {
        return calc_scroll_percent_increment();
    }
};

export default get_scroll_percentage;
