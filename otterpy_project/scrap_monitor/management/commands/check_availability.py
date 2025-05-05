import os
from django.core.management.base import BaseCommand
from scrap_monitor.scraper_db import check_availability, get_availability
from dotenv import load_dotenv
load_dotenv()
class Command(BaseCommand):
    help = 'Check Sanparks Otter Trail availability and send email notifications for new spots'
    
    def handle(self, *args, **options):
        success, message = check_availability()
        
        if success:
            self.stdout.write(self.style.SUCCESS('New availability found! Email notification sent.'))
            self.stdout.write(message)
        else:
            if message:
                self.stdout.write(self.style.ERROR(f'Error: {message}'))
            else:
                self.stdout.write(self.style.WARNING('No new availability found.'))
