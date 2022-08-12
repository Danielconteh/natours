from django.contrib import admin

from .models import Location, Tour,Images,Review,Tour_Guide,Booked_Tour

 
class ImagesAdmin(admin.StackedInline):
    model = Images
 
@admin.register(Tour)
class PostAdmin(admin.ModelAdmin):
    inlines = [ImagesAdmin]
    prepopulated_fields = {"slug":("name",)}
    
 
    class Meta:
       model = Tour
 
admin.site.register(Location)
admin.site.register(Images)
admin.site.register(Review)
admin.site.register(Tour_Guide) 
admin.site.register(Booked_Tour) 




