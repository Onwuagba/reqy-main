from django.contrib import admin
from .models import Department, DepartmentUser, Organisation, OrganisationUser, User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone_number')

admin.site.register  (Organisation)
admin.site.register  (Department)

@admin.register(OrganisationUser)
class OrgUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'org_id', 'role', 'added_on', 'added_by')

@admin.register(DepartmentUser)
class OrgUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'department_id', 'added_on', 'created_by')