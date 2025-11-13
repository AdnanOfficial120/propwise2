from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
import json
import datetime

# --- 1. ALL MODEL IMPORTS ---
from .models import City, Area, Amenity, Question, Answer
from properties.models import Property, PropertyStatus 

# --- 2. ALL HELPER IMPORTS ---
from django.db.models import Avg, F, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from django.utils import timezone
from decimal import Decimal

# --- 3. NEW IMPORTS FOR Q&A FORMS/ACTIONS ---
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import QuestionForm, AnswerForm


def all_cities_view(request):
    """
    Page 1: Displays a list of all cities.
    """
    cities = City.objects.all().order_by('name')
    context = {
        'cities': cities
    }
    return render(request, 'locations/all_cities.html', context)


def city_detail_view(request, city_pk):
    """
    Page 2: Displays details for one city, including all its areas.
    """
    city = get_object_or_404(City, pk=city_pk)
    areas_in_city = city.areas.all().order_by('name')
    context = {
        'city': city,
        'areas': areas_in_city
    }
    return render(request, 'locations/city_detail.html', context)


# --- THIS IS YOUR NEW, FULLY UPGRADED VIEW ---
def area_detail_view(request, area_pk):
    """
    Page 3: Displays all properties for a specific area,
    PLUS Neighborhood Insights, "What's Nearby" data,
    AND the new "Price Trends" chart and "Community Q&A".
    """
    
    # 1. Get the specific area
    area = get_object_or_404(Area, pk=area_pk)
    
    # 2. Get all *ACTIVE* properties in this area
    properties_in_area = Property.objects.filter(
        area=area,
        status=PropertyStatus.ACTIVE
    ).order_by('-created_at')
    
    # 3. Get all amenities and group them by type (for the list)
    all_amenities = area.amenities.all().order_by('amenity_type', 'name')
    amenities_by_type = {}
    
    # 4. Create a JSON list of amenities *for the map*
    amenities_for_map = []
    for amenity in all_amenities:
        type_name = amenity.get_amenity_type_display()
        if type_name not in amenities_by_type:
            amenities_by_type[type_name] = []
        amenities_by_type[type_name].append(amenity)
        
        if amenity.latitude and amenity.longitude:
            map_details = amenity.get_map_details()
            amenities_for_map.append({
                'name': amenity.name,
                'type': amenity.get_amenity_type_display(),
                'lat': float(amenity.latitude),
                'lng': float(amenity.longitude),
                'icon': map_details['icon'],
                'color': map_details['color']
            })
            
    # --- 5. "PRICE TRENDS" LOGIC (Price Per SqFt) ---
    one_year_ago = timezone.now() - datetime.timedelta(days=365)
    marla_to_sqft = Decimal('272.25')
    kanal_to_sqft = Decimal('5445.0')
    sqyard_to_sqft = Decimal('9.0')
    
    sold_properties = Property.objects.filter(
        area=area,
        status=PropertyStatus.SOLD,
        sold_date__gte=one_year_ago,
        price__gt=0
    ).exclude(area_size=0)

    price_data = sold_properties.annotate(
        size_in_sqft=Case(
            When(area_unit='marla', then=F('area_size') * marla_to_sqft),
            When(area_unit='kanal', then=F('area_size') * kanal_to_sqft),
            When(area_unit='sq_yard', then=F('area_size') * sqyard_to_sqft),
            When(area_unit='sq_ft', then=F('area_size') * Decimal('1.0')),
            default=F('area_size'),
            output_field=DecimalField()
        ),
        price_per_sqft=F('price') / F('size_in_sqft')
    ).annotate(
        month=TruncMonth('sold_date')
    ).values('month').annotate(avg_price=Avg('price_per_sqft')).order_by('month')
    
    price_chart_labels = []
    price_chart_data = []
    
    if price_data.count() > 1:
        for item in price_data:
            price_chart_labels.append(item['month'].strftime('%b %Y'))
            # Convert Decimal to float for JSON
            price_chart_data.append(float(item['avg_price']))
            
    # --- 6. NEW: "COMMUNITY Q&A" LOGIC ---
    
    # Get all questions for this area
    # Prefetch answers and users to prevent N+1 queries
    questions = area.questions.all().prefetch_related(
        'answers', 
        'answers__user'
    )
    
    # Create empty forms to pass to the template
    question_form = QuestionForm()
    answer_form = AnswerForm()

    # --- 7. Build the final context ---
    context = {
        'area': area,
        'properties': properties_in_area,
        'amenities_by_type': amenities_by_type,
        'amenities_json': json.dumps(amenities_for_map),
        'price_chart_labels': json.dumps(price_chart_labels),
        'price_chart_data': json.dumps(price_chart_data),
        
        # --- ADD NEW Q&A DATA TO CONTEXT ---
        'questions': questions,
        'question_form': question_form,
        'answer_form': answer_form,
    }
    
    return render(request, 'locations/area_detail.html', context)


def ajax_load_areas(request):
    """
    An "API" view that returns a list of areas for a given city_id.
    """
    city_id = request.GET.get('city_id')
    if city_id:
        areas = Area.objects.filter(city_id=city_id).order_by('name')
        data = [{'id': area.id, 'name': area.name} for area in areas]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


# --- START: NEW Q&A "ACTION" VIEWS ---

@login_required
@require_POST
def add_question_view(request, area_pk):
    """
    Handles the POST submission for a new Question.
    """
    area = get_object_or_404(Area, pk=area_pk)
    form = QuestionForm(request.POST)
    
    if form.is_valid():
        question = form.save(commit=False)
        question.area = area
        question.user = request.user
        question.save()
        messages.success(request, "Your question has been posted!")
    else:
        messages.error(request, "There was an error with your question. Please check the form.")
        
    # Redirect back to the area page, no matter what
    return redirect('area_detail', area_pk=area.pk)


@login_required
@require_POST
def add_answer_view(request, question_pk):
    """
    Handles the POST submission for a new Answer.
    """
    question = get_object_or_404(Question, pk=question_pk)
    form = AnswerForm(request.POST)
    
    if form.is_valid():
        answer = form.save(commit=False)
        answer.question = question
        answer.user = request.user
        answer.save()
        messages.success(request, "Your answer has been posted!")
    else:
        messages.error(request, "Your answer could not be empty.")
    
    # Redirect back to the area page this question lives on
    return redirect('area_detail', area_pk=question.area.pk)

# --- END: NEW Q&A "ACTION" VIEWS ---