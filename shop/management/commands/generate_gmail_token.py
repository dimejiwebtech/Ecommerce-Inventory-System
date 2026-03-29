import os

from django.core.management.base import BaseCommand, CommandError

from utils.generate_credentials import GmailCredentialsManager

# Allow HTTP redirect for local development OAuth flow
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


class Command(BaseCommand):
    help = 'Generate Gmail API OAuth2 token'
    
    def handle(self, *args, **options):
        credentials_manager = GmailCredentialsManager()
        
        try:
            self.stdout.write("Starting Gmail OAuth2 flow...")
            creds = credentials_manager.generate_new_token()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Gmail token generated successfully! "
                    f"Gmail token generated successfully and saved to database!"
                )
            )
            
        except FileNotFoundError as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(f"Failed to generate token: {e}")