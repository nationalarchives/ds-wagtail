import add_analytics_data_card_position from './modules/analytics/card_position'
import audio_tracking from "./modules/analytics/audio_tracking"
import video_tracking from "./modules/analytics/video_tracking"
import add_unique_ids from "./modules/analytics/add_unique_ids";

import accordion_functionality from "./modules/insights/accordion_functionality/accordion_functionality";
import add_event from "./modules/insights/add_event";
import add_section_ids from "./modules/insights/accordion_functionality/add_section_ids";
import apply_aria_roles from "./modules/insights/accordion_functionality/apply_aria_roles";
import debounce from "./modules/debounce";
import jumplinks_smooth_scroll from './modules/insights/navigation/jumplinks_smooth_scroll';
import open_first_section from "./modules/insights/accordion_functionality/open_first_section";
import remove_aria_roles from "./modules/insights/accordion_functionality/remove_aria_roles";
import remove_event from "./modules/insights/remove_event";
import set_active from "./modules/insights/navigation/set_active";
import throttle from "./modules/throttle";

document.addEventListener('DOMContentLoaded', () => {
    const $sectionHeadings = $(".section-separator__heading");
    const $sectionContents = $(".section-content");
    const $jumplinks = $(".jumplink");
    const $windowWidth = $(window).width();

    // This boolean is used to detect if certain enhancements (e.g. click event listeners) have been applied in order to 
    // prevent events from being added more than once.
    let mobileEnhancementsApplied = false;

    add_analytics_data_card_position('.record-embed-no-image');
    add_analytics_data_card_position('.card-group-secondary-nav');
    audio_tracking();
    video_tracking();
    add_unique_ids();

    // Ids are added to sections for ARIA purposes.
    add_section_ids($sectionHeadings, $sectionContents);

    if($windowWidth < 768 && !mobileEnhancementsApplied) {
        apply_aria_roles($sectionHeadings, $sectionContents);

        // Detect if there are any expanded sections. If not, expand the first section.
        open_first_section($sectionHeadings, $sectionContents);

        // Add click and enter listeners for expanding/collapsing sections on small screens.
        add_event($sectionHeadings, "click", function() {
            accordion_functionality(this, $sectionHeadings, $sectionContents)
        });
        add_event($sectionHeadings, "keypress", function(e) {
            if(e.which === 13 || e.which === 32) {
                accordion_functionality(this, $sectionHeadings, $sectionContents)
            }
        });
        mobileEnhancementsApplied = true;
    }
    else if(!mobileEnhancementsApplied) {
        // Add click and scroll listeners for smooth scrolling when using jumpinks to navigate the page and 
        // progress indication in the navigation on desktop.
        add_event($(window), "scroll", throttle(function() {
            set_active($sectionHeadings)
        }, 300))
        add_event($jumplinks, "click", function() {
            jumplinks_smooth_scroll(this);
        })
    }

    $(window).on('resize', debounce(() => {
        if($(window).width() < 768 && !mobileEnhancementsApplied){
            apply_aria_roles($sectionHeadings, $sectionContents);

            // Detect if there are any expanded sections. If not, expand the first section.
            open_first_section($sectionHeadings, $sectionContents);

            // Add click and enter listeners for expanding/collapsing sections when the screen size is reduced.
            add_event($sectionHeadings, "click", function() {
                accordion_functionality(this, $sectionHeadings, $sectionContents)
            });
            add_event($sectionHeadings, "keypress", function(e) {
                if(e.which === 13 || e.which === 32) {
                    accordion_functionality(this, $sectionHeadings, $sectionContents)
                }
            });

            // Remove scroll listener
            remove_event($(window), "scroll");

            mobileEnhancementsApplied = true;
        }
        else if ($(window).width() >= 768) {
            remove_aria_roles($sectionHeadings);

            // Remove click and enter listeners because sections are fully expanded on desktop 
            // i.e. no accordion functionality required.
            remove_event($sectionHeadings, "click");
            remove_event($sectionHeadings, "keypress");

            // Add click and scroll listeners for smooth scrolling when using jumpinks to navigate the page and 
            // progress indication in the navigation when the screen size is increased.
            add_event($jumplinks, "click", function() {
                jumplinks_smooth_scroll(this)
            })
            add_event($(window), "scroll", throttle(function() {
                set_active($sectionHeadings)
            }, 300))
            mobileEnhancementsApplied = false;
        }
    }, 200));
});
