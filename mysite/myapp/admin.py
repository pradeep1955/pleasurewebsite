from django.contrib import admin

# Register your models here.

from .models import Contact

admin.site.register(Contact)

from .models import Visitor

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'user_agent', 'visit_time')
    list_filter = ('visit_time',)
