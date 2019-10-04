from django.contrib import admin

from dashboard.models import UploadFileModel, CustomUserModel, FileColumnModel


class FileColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'column', 'type', 'dependence')
    list_display_links = ('id', 'column')
    list_filter = ('type', 'dependence')
    list_editable = ('type', 'dependence')
    search_fields = ('file', 'type', 'dependence')
    list_per_page = 25

# admin.site.register(Contact, ContactAdmin)


admin.site.register(UploadFileModel)
admin.site.register(CustomUserModel)
admin.site.register(FileColumnModel, FileColumnAdmin)
