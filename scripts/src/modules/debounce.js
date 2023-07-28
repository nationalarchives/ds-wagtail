/**
 *
 * Invoke a given callback after debounce function
 * hasn't been called for a specified number of milliseconds
 *
 * usage:
 * debounce( call_back, 500 )( ..arg );
 *
 * @param {Function} call_back
 * @param {Number} wait
 * @param {Object} this_argument
 **/

export default function (call_back, wait, this_argument) {
    var timer = null;

    return function (...args) {
        var context = this_argument || this;

        window.clearTimeout(timer);

        timer = window.setTimeout(() => {
            timer = null;

            call_back.apply(context, args);
        }, wait);
    };
}
