import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import EventPage, WhatsOnPage, EventType
from etna.images.models import CustomImage

@csrf_exempt
def eventbrite_webhook_view(request):
    if request.method == 'POST':
        # Parse the JSON data from the request
        json_data = json.loads(request.body)

        # Process the Eventbrite data


        # Create draft EventPage
        whats_on_page = WhatsOnPage.objects.get(title="What's On")
        random_image = CustomImage.objects.order_by('?').first()
        random_event_type = EventType.objects.order_by('?').first()
        event_page = EventPage(title=json_data["title"], teaser_text="Test teaser text", intro="Test intro", short_title="Test short title", event_type=random_event_type, venue_address="Test address", venue_space_name="Yes", lead_image=random_image, live=False)

        whats_on_page.add_child(instance=event_page)

        # Return a response indicating successful processing of the webhook
        return JsonResponse({'success': 'success'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)