import $ from 'jquery';

import add_analytics_data_card_position from './modules/analytics/card_position'
import audio_tracking from "./modules/analytics/audio_tracking"
import video_tracking from "./modules/analytics/video_tracking"
import add_unique_ids from "./modules/analytics/add_unique_ids";
import mobile_tracking from "./modules/analytics/insights_tracking/mobile_tracking";
import remove_mobile_tracking from "./modules/analytics/insights_tracking/remove_mobile_tracking";
import link_list_tracking from "./modules/analytics/insights_tracking/link_list_tracking";

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
import set_heading_positions from "./modules/insights/accordion_functionality/set_heading_positions";
import throttle from "./modules/throttle";

document.addEventListener('DOMContentLoaded', () => {
    add_analytics_data_card_position('.record-embed-no-image');
    add_analytics_data_card_position('.card-group-secondary-nav > a');
    add_analytics_data_card_position('.card-group-secondary-nav__body > a');
    audio_tracking();
    video_tracking();
    add_unique_ids();
    link_list_tracking();
});

window.addEventListener('load', () => {
    // Initialise jquery
    window.$ = $;

    const $sectionHeadings = $(".section-separator__heading");
    const $sectionContents = $(".section-content");
    const $jumplinks = $(".jumplink");
    const baseFontSize = 16;
    const remScreenSize = 48;
    let headingPositions;

    // These booleans are used to detect if certain enhancements (e.g. click event listeners) have been applied in order to 
    // prevent events from being added more than once.
    let mobileEnhancementsApplied = false;
    let desktopEnhancementsApplied = false;

    // Ids are added to sections for ARIA purposes.
    add_section_ids($sectionHeadings, $sectionContents);
    
    if($(window).width() / baseFontSize <= remScreenSize && !mobileEnhancementsApplied) {
        $sectionContents.hide();
        apply_aria_roles($sectionHeadings, $sectionContents);

        // Detect if there are any expanded sections. If not, expand the first section.
        open_first_section($sectionHeadings, $sectionContents);

        // Obtain the positions of the headings. These are used for keeping a heading at the top of the viewport when
        // it's corresponding section is expanded.
        headingPositions = set_heading_positions($sectionHeadings);

        // Add click and enter listeners for expanding/collapsing sections on small screens.
        add_event($sectionHeadings, "click", function() {
            accordion_functionality(this, $sectionHeadings, $sectionContents, headingPositions);
        });
        add_event($sectionHeadings, "keypress", function(e) {
            if(e.key === "Enter") {
                accordion_functionality(this, $sectionHeadings, $sectionContents, headingPositions);
            }
        });

        mobile_tracking();

        mobileEnhancementsApplied = true;
    }
    else if(!desktopEnhancementsApplied) {
        // Add click and scroll listeners for smooth scrolling when using jumpinks to navigate the page and 
        // progress indication in the navigation on desktop.
        add_event($(window), "scroll", throttle(function() {
            set_active($sectionHeadings);
        }, 300));
        add_event($jumplinks, "click", function() {
            jumplinks_smooth_scroll(this);
        });

        $sectionContents.show();

        desktopEnhancementsApplied = true;
    }

    $(window).on('resize', debounce(() => {
        if($(window).width() / baseFontSize <= remScreenSize && !mobileEnhancementsApplied){
            $sectionContents.hide();
            apply_aria_roles($sectionHeadings, $sectionContents);

            open_first_section($sectionHeadings, $sectionContents);

            headingPositions = set_heading_positions($sectionHeadings);

            // Remove scroll and jumplink click listeners
            remove_event($(window), "scroll");
            remove_event($jumplinks, "click");

            add_event($sectionHeadings, "click", function() {
                accordion_functionality(this, $sectionHeadings, $sectionContents, headingPositions);
            });
            add_event($sectionHeadings, "keypress", function(e) {
                if(e.key === "Enter") {
                    accordion_functionality(this, $sectionHeadings, $sectionContents, headingPositions);
                }
            });

            mobile_tracking();

            desktopEnhancementsApplied = false;
            mobileEnhancementsApplied = true;
        }
        else if($(window).width() / baseFontSize <= remScreenSize && mobileEnhancementsApplied) {
            // Recalculate heading positions on resize.
            headingPositions = set_heading_positions($sectionHeadings);
        }
        else if ($(window).width() / baseFontSize > remScreenSize && !desktopEnhancementsApplied) {
            remove_aria_roles($sectionHeadings);

            // Remove click and enter listeners because sections are fully expanded on desktop 
            // i.e. no accordion functionality required.
            remove_event($sectionHeadings, "click");
            remove_event($sectionHeadings, "keypress");

            // Add click and scroll listeners for smooth scrolling when using jumpinks to navigate the page and 
            // progress indication in the navigation when the screen size is increased.
            add_event($(window), "scroll", throttle(function() {
                set_active($sectionHeadings);
            }, 300));
            add_event($jumplinks, "click", function() {
                jumplinks_smooth_scroll(this);
            });

            $sectionContents.show();

            remove_mobile_tracking();
            
            desktopEnhancementsApplied = true;
            mobileEnhancementsApplied = false;
        }
    }, 200));
});