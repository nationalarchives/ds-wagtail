from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Manage 2FA devices." #TODO make better


    def add_arguments(self, parser):

    	parser.add_argument("--target-email", required=True, help="Email of the user to be reset.")
    	parser.add_argument("--admin-username", required=True, help="Admin/username performing reset.")
        parser.add_argument("--reason", default="Your 2FA devices have been removed from your account. Please reset your password. /n Note: Any active sessions you may have had have also been deleted.",  help="Optional reason to include in the notification email")

	
	#be authenticated with an admin account
	def admin_authentication():




	# remove all 2FA devices
	def remove_devices():



	# reset the password
	def reset_password():



	# remove all active sessions for that user
	def remove_all_active_sessions():



	# send them an email
	def send_email():



    def handle(self, *args, **options):
        target_email = options["target_email"].strip().lower()
        admin_username = options["admin_username"].strip()
        reason = options["reason"]

        self._list_tokens(quiet)

