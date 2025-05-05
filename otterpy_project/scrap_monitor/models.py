from django.db import models

# Create your models here if needed
class LastScrap(models.Model):
    """Model to store the last scraping data"""
    last_scrap = models.TextField(default="0,0,0,0")
    
    def __str__(self):
        return f"LastScrap ID: {self.id}"
    
    @classmethod
    def get_last_scrap(cls):
        """Get the last scrap data or create if it doesn't exist"""
        last_scrap, created = cls.objects.get_or_create(id=1)
        return last_scrap.last_scrap
    
    @classmethod
    def update_last_scrap(cls, new_data):
        """Update the last scrap data"""
        last_scrap, created = cls.objects.get_or_create(id=1)
        last_scrap.last_scrap = new_data
        last_scrap.save()
