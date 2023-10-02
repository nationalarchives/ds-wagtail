import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def eventbrite_webhook_view(request):
    if request.method == 'POST':
        # Parse the JSON data from the request

        # Return a response indicating successful processing of the webhook
        return JsonResponse({'success': 'success'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)