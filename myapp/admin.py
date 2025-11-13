# contacts/admin.py
from django.contrib import admin
# Import all your models at the top for cleanliness
from .models import Contact, Hotel, Visitor, DailyMessage, Video

# Register models with the default admin interface
admin.site.register(Contact)
admin.site.register(Hotel)
admin.site.register(DailyMessage)
admin.site.register(Video) # Register the new Video model
# Register the Visitor model with your custom ModelAdmin class
@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'user_agent', 'visit_time')
    list_filter = ('visit_time',)
