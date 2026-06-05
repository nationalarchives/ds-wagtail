from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Manage 2FA devices." #TODO make better

#TODO copoied from api listing for skeleton
    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         "--quiet",
    #         action="store_true",
    #         help="Don't print human-readable output, just the token key (for create/refresh)",
    #     )



    # def _list_tokens(self, quiet=False):
    #     tokens = APIToken.objects.all()
    #     if tokens:
    #         if not quiet:
    #             self.stdout.write(self.style.SUCCESS("API tokens:"))
    #         for token in tokens:
    #             self.stdout.write(
    #                 f"- {token.name}{' (active)' if token.active else ' (inactive)'}"
    #             )
    #     else:
    #         self.stdout.write("No API tokens found.")



    # def handle(self, *args, **options):
    #     quiet = options["quiet"]

    #     self._list_tokens(quiet)

