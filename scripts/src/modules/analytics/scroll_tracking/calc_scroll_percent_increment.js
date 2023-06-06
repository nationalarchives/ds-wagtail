const pageHeight = document.documentElement;
const body = document.body;
const scrollTop = "scrollTop";
const scrollHeight = "scrollHeight";

const calc_scroll_percent_increment = () => {
    const scrollPercentage = Math.floor(
        ((pageHeight[scrollTop] || body[scrollTop]) /
            ((pageHeight[scrollHeight] || body[scrollHeight]) -
                pageHeight.clientHeight)) *
            100
    );

    if (scrollPercentage < 25) {
        return 0;
    } else if (scrollPercentage < 50) {
        return 25;
    } else if (scrollPercentage < 75) {
        return 50;
    } else if (scrollPercentage < 100) {
        return 75;
    } else {
        return 100;
    }
};

export default calc_scroll_percent_increment;
