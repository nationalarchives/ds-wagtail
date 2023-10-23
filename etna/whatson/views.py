import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def eventbrite_webhook_view(request):
    if request.method == "POST":
        # Parse the JSON data from the request
        # json_data = json.loads(request.body)

        # Process the Eventbrite data

        # Create draft EventPage

        # Return a response indicating successful processing of the webhook
        return JsonResponse({"success": "success"}, status=200)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
