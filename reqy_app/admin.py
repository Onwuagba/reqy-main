from django.contrib import admin
from .models import Comment, Format, Reminder, ReqApprover, ReqFile, ReqItem, ReqRepeat, Requisition, ReqFormat

# Register your models here.
@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'date_created', 'dateUpdated')

admin.site.register  (Format)
admin.site.register  (ReqFormat)
admin.site.register  (ReqItem)
admin.site.register  (ReqApprover)
admin.site.register  (ReqFile)
admin.site.register  (ReqRepeat)
admin.site.register  (Comment)
admin.site.register  (Reminder)