from django.contrib.gis import admin
from data_annotator.models import Samplesproject, Image, Shape, Site, Label, Macroproject, Profile


class LabelInline(admin.StackedInline):
    model = Label


class SamplesProjectAdmin(admin.ModelAdmin):
    list_display = ("project_name", "place_name", "local_site", "start_date", "producer", "client")
    list_display_links = ("project_name", "place_name", "local_site", "start_date", "producer", "client")
    date_hierarchy = "start_date"


class MacroProjectAdmin(admin.ModelAdmin):
    inlines = [
        LabelInline,
    ]
    list_display = ('macro_project_name', 'start_date')


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'cellphone', 'Phone', 'institution', 'province', 'municipality', 'speciality', 'is_manager',
        'is_annotator',
        'is_operator', 'is_contact')
    list_display_links = (
        'user', 'cellphone', 'Phone', 'institution', 'province', 'municipality', 'speciality', 'is_manager',
        'is_annotator',
        'is_operator', 'is_contact')


class SiteAdmin(admin.ModelAdmin):
    list_display = ['sample_project']
    ordering = ['sample_project']


admin.site.register(Site, SiteAdmin)
admin.site.register(Samplesproject, SamplesProjectAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Label)
admin.site.register(Image)
admin.site.register(Shape)
admin.site.register(Macroproject, MacroProjectAdmin)
