# locations/admin.py

from django.contrib import admin
# --- 1. IMPORT YOUR NEW 'Question' AND 'Answer' MODELS ---
from .models import City, Area, Amenity, Question, Answer

# Register your models here.

# We will keep the City admin simple
admin.site.register(City)


class AmenityInline(admin.TabularInline):
    """
    This allows us to add/edit Amenities directly from the Area admin page.
    """
    model = Amenity
    fields = ('name', 'amenity_type', 'latitude', 'longitude')
    extra = 1 
    classes = ('collapse',) 


# --- 2. CREATE A NEW "INLINE" CLASS FOR QUESTIONS ---
class QuestionInline(admin.StackedInline):
    """
    This allows us to see (but not add) Questions
    directly from the Area admin page.
    'StackedInline' gives it more room than a table.
    """
    model = Question
    fields = ('title', 'user', 'body', 'created_at')
    readonly_fields = ('title', 'user', 'body', 'created_at') # Make them read-only here
    extra = 0 # Don't show "add new" boxes here
    can_delete = False # Don't allow deleting questions from the Area page
    classes = ('collapse',) # Make it collapsible


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """
    Custom admin options for the Area model.
    """
    list_display = (
        'name', 
        'city', 
        'latitude', 
        'longitude',
    )
    list_filter = ('city',)
    search_fields = ('name', 'city__name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'city')
        }),
        ('Neighborhood Insights (Optional)', {
            'classes': ('collapse',),
            'description': 'Add the area description and map coordinates here.',
            'fields': (
                'description', 
                'latitude', 
                'longitude'
            ),
        }),
    )
    
    # --- 3. ADD BOTH INLINES TO YOUR 'AreaAdmin' ---
    inlines = [AmenityInline, QuestionInline]


# --- 4. CREATE A NEW ADMIN FOR THE 'Question' MODEL ---
class AnswerInline(admin.TabularInline):
    """
    This allows us to see and add Answers
    directly from the Question admin page.
    """
    model = Answer
    fields = ('user', 'body', 'created_at')
    readonly_fields = ('created_at',)
    extra = 1

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Custom admin options for the Question model.
    """
    list_display = ('title', 'area', 'user', 'created_at')
    list_filter = ('area__city', 'area')
    search_fields = ('title', 'body', 'user__username', 'area__name')
    readonly_fields = ('created_at',)
    
    # This will show all Answers at the bottom of the Question's edit page
    inlines = [AnswerInline]


# --- 5. REGISTER THE 'Answer' MODEL (Optional but good) ---
# This just lets you see a master list of all answers
admin.site.register(Answer)