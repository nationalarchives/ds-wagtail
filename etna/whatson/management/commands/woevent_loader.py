from django.core.management.base import BaseCommand
import re
import pprint
from datetime import datetime
from ...models import EventType, EventPage, VenueType

from eventbrite import Eventbrite

EVENTBRITE_PRIVATE_TOKEN="5NB2D6KB5WI7M4FGA7DW"
EVENTBRITE_TNA_ORGANISATION_ID="32190014757"
EVENTBRITE_EVENTS_EXPANSION="description,category,organizer,venue,format,ticket_classes,ticket_class_id,ticket_buyer_settings"

baseurl = "https://www.eventbriteapi.com/v3/"

# Extend the eventbrite SDK class as it has useful connectivity functionality but doesn't return the data in the format we require.
class TNAEventbrite(Eventbrite):
    def __init__(self, authkey):
        super().__init__(authkey)

    def get_event_list(self, org_id, continuation=None, **data):

        if continuation:
            #return self.get(f"/organizations/{org_id}/events/?expand.event=organizer,venue&time_filter=current_future&order_by=start_desc&status=live,draft,started&continuation={continuation}", data=data)
            return self.get(f"/organizations/{org_id}/events/?page_size=200&time_filter=current_future&order_by=start_desc&status=live,draft,started&organizer_filter=2226699547&continuation={continuation}", data=data)
        else:
            return self.get(f"/organizations/{org_id}/events/?page_size=200&time_filter=current_future&order_by=start_desc&status=live,draft,started&organizer_filter=2226699547", data=data)
        
    def get_description(self, event_id, **data):
        return self.get(f"/events/{event_id}/description", data=data)
    
    def get_capacity_tier(self, event_id, **data):
        return self.get(f"/events/{event_id}/capacity_tier", data=data)
    
    def get_teams(self, event_id, **data):
        return self.get(f"/events/{event_id}/teams", data=data)
    
    def get_questions(self, event_id, **data):
        return self.get(f"/events/{event_id}/questions", data=data)
    


    
def get_prices_minmax(ticket_classes):
    mintp = 12345.67
    maxtp = 0.0

    for tp in ticket_classes:
        if tp.get('cost'):
            if float(tp['cost']['major_value']) < mintp:
                mintp = float(tp['cost']['major_value'])
            if float(tp['cost']['major_value']) > maxtp:
                maxtp = float(tp['cost']['major_value'])

    if mintp == 12345.67:
        mintp = 0.0

    return mintp, maxtp

def populate_event_data(event, event_description):
    pattern = re.compile('<.*?>')
    event_data = {}

    event_data['description'] = re.sub(pattern, ' ', event_description.get('description'))

    event_data['lead_image_fk'] = 'TBC'
    event_data['event_type_fk'] = 'TBC'
    event_data['event_type'] = event['format']['short_name']

    event_data['start_date'] = datetime.strptime(event['start']['local'], "%Y-%m-%dT%H:%M:%S") #'2024-03-15T14:00:00' 
    event_data['end_date'] = datetime.strptime(event['end']['local'], "%Y-%m-%dT%H:%M:%S") #'2024-03-15T14:00:00'
    event_data['useful_info'] = 'TBC'
    event_data['target_audience'] = 'TBC'

    if event['venue']: # value always there but may be None
        if not event['online_event']:
            # Assume that the event is IN_PERSON as there is an address but online event flag is False
            event_data['venue_type'] = VenueType.IN_PERSON
        else:
            # Assume that the event is HYBRID as there is an address and online event flag is True
            event_data['venue_type'] = VenueType.HYBRID

        event_data['venue_website'] = event['organizer']['website']
        event_data['venue_address'] = event['venue']['address']['localized_address_display']
        event_data['venue_space_name'] = event['venue']['name']
    else:
        if not event['online_event']:
            # Assume that the event is TBA as there is no address and online event flag is False
            event_data['venue_type'] = VenueType.TBA
        else:
            # Assume that the event is ONLINE as there is no address and online event flag is True
            event_data['venue_type'] = VenueType.ONLINE

        event_data['venue_website'] = ''
        event_data['venue_address'] = ''
        event_data['venue_space_name'] = ''
                        
    event_data['video_conference_info'] = 'TBC'
    event_data['registration_url'] = event['url']

    if event.get('ticket_classes', False): # value may not be in the dict
        event_data['min_price'], event_data['max_price'] = get_prices_minmax(event['ticket_classes'])

    event_data['eventbrite_id'] =  event['id']
    event_data['registration_info'] = 'TBC'
    event_data['contact_info'] = 'TBC'
    event_data['short_title'] = event['name']['text']

    return event_data
                    
def populate_capacity_tier(capacity):
    capacity_data = {}

    if capacity:
        capacity_data['total'] = capacity['capacity_total']
        capacity_data['sold'] = capacity['capacity_sold']
        capacity_data['pending'] = capacity['capacity_pending']

    return capacity_data

def populate_teams(teams):
    team_data = {}

    if teams:
        for t in teams['teams']:
            print(f"Teams is {t}")
            #team_data['name'] = teams.teams[0]['name']

    return team_data

def populate_questions(questions):
    question_data = {}

    if questions:
        print(f"Questions: {questions}")
        #for q in questions:
        #    print(f"Question: {q[0]}")
            #team_data['name'] = teams.teams[0]['name']

    return question_data

def display_data():
    all_events = EventPage.objects.all().values()

    print(f"All Events: {all_events}")

def save_event_page(event):
    e = EventPage(  start_date=event['start_date'],
                    end_date=event['end_date'],
                    description=event['description'],
                    useful_info=event['useful_info'],
                    target_audience=event['target_audience'],
                    venue_type=event['venue_type'],
                    venue_website=event['venue_website'],
                    venue_address=event['venue_address'],
                    venue_space_name=event['venue_space_name'],
                    video_conference_info=event['video_conference_info'],
                    registration_url=event['registration_url'],
                    min_price=event['min_price'],
                    max_price=event['max_price'],
                    eventbrite_id=event['eventbrite_id'],
                    registration_info=event['registration_info'],
                    contact_info=event['contact_info'],
                    short_title=event['short_title'])
    e.save()



class Command(BaseCommand):
    help = "Fetch data from Eventbrite TNA api and store in database"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--dry",
            action="store_true",
            help="Don't save to the database, just print data instead",
        )

    def handle(self, *args, **kwargs):
        debug = 2
        dryrun = kwargs['dry'] or None

        try:
            eventbrite = TNAEventbrite(EVENTBRITE_PRIVATE_TOKEN)

            evs = eventbrite.get_event_list(org_id = EVENTBRITE_TNA_ORGANISATION_ID,
                                            expand=EVENTBRITE_EVENTS_EXPANSION)        
            if debug == 2:
                print(evs.pretty)
        except:
            pass

        # We are expecting a json response with two components: a pagination block and a list of events.
        eventlist  = evs['events']
        pagination = evs['pagination']

        # Now loop through the events
        while True:
            for event in eventlist:
                # For each event, get the following fields - these can't be obtained by using the expand feature unfortunately.
                desc      = eventbrite.get_description(event['id'])
                capacity  = eventbrite.get_capacity_tier(event['id'])
                teams     = eventbrite.get_teams(event['id'])
                questions = eventbrite.get_questions(event['id'])

                # Save required data in new dictionary
                event_data = populate_event_data(event, desc)
                event_data['capacity_data'] = populate_capacity_tier(capacity)
                event_data['team_data'] = populate_teams(teams)
                event_data['questions'] = populate_questions(questions)

                if debug:
                    #pprint.pprint(event_data)
                    print(f"Venue URL: {event_data['venue_website']}")

                save_event_page(event_data)

                if debug == 1:
                    print(f"ID: {event['id']}#" \
                            f"{event['start']['local']}#" \
                            f"{event['hide_start_date']:{1}}#" \
                            f"{event['hide_end_date']:{1}}#" \
                            f"{event['is_externally_ticketed']:{1}}#" \
                            f"{event['is_free']:{1}}#" \
                            f"{event['is_locked']:{1}}#" \
                            f"{event['is_reserved_seating']:{1}}#" \
                            f"{event['is_series']:{1}}#" \
                            f"{event['is_series_parent']:{1}}#" \
                            f"{event['listed']:{1}}#" \
                            f"{event.get('logo_id', '?'):{10}}#" \
                            f"{event.get('organizer_id', '?'):{10}}#" \
                            f"{event.get('privacy_setting', '?'):{8}}#" \
                            f"{event['name']['text']}")

                #if e['is_series']:
                #    ser = eventbrite.get_event_series(e['series_id'])

                #    if (e['id'] == "698469429867"):
                #        print(f"  ==> Series: {ser.pretty}")

                #if e['id'] == "638107746447":
                #    print(e)

            if pagination['has_more_items']:
                evs = eventbrite.get_event_list(org_id = EVENTBRITE_TNA_ORGANISATION_ID,
                                                continuation=pagination['continuation'],
                                                expand=EVENTBRITE_EVENTS_EXPANSION)

                if debug == 2:
                    print(evs.pretty)

                eventlist  = evs['events']
                pagination = evs['pagination']
                
                if debug:
                    print(pagination)
            else:
                break

        display_data()

