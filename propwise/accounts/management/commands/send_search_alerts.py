# accounts/management/commands/send_search_alerts.py

import logging
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal

from accounts.models import SavedSearch, User
from properties.models import Property
from django.conf import settings

# Set up logging to see output in your console
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Finds new properties matching saved searches and sends email alerts.'

    def handle(self, *args, **options):
        
        # --- IMPORTANT: SET YOUR DOMAIN ---
        # For testing on your computer, use this:
        DOMAIN = '127.0.0.1:8000'
        # When you deploy to a real website, change this to:
        # DOMAIN = 'www.propwise.com'
        # ---

        self.stdout.write(f"[{timezone.now()}] Starting send_search_alerts...")

        # 1. Get all active saved searches
        active_searches = SavedSearch.objects.filter(is_active=True)
        
        if not active_searches.exists():
            self.stdout.write("No active saved searches found.")
            return

        total_emails_sent = 0

        # 2. Loop through each saved search
        for search in active_searches:
            user = search.user
            
            # --- 3. Build a dynamic filter based on the saved search criteria ---
            # This is the "brain" of the operation.
            
            # Start with a base filter:
            # Only find properties that are *newer* than the last time we checked.
            filters = Q(created_at__gt=search.last_checked)

            # Add more filters only if the user saved them
            if search.city:
                # We use 'area__city' just like in your PropertyFilter
                filters &= Q(area__city=search.city)
            
            if search.keyword:
                filters &= Q(title__icontains=search.keyword)
                
            if search.property_type:
                filters &= Q(property_type=search.property_type)
                
            if search.purpose:
                filters &= Q(purpose=search.purpose)

            # --- Price and Bedroom Filters ---
            if search.min_price:
                # 'gte' means "Greater Than or Equal to"
                filters &= Q(price__gte=search.min_price)
                
            if search.max_price:
                # 'lte' means "Less Than or Equal to"
                filters &= Q(price__lte=search.max_price)

            if search.min_bedrooms:
                filters &= Q(bedrooms__gte=search.min_bedrooms)
            
            # --- 4. Run the query to find matching new properties ---
            try:
                new_properties = Property.objects.filter(filters).distinct()

                if new_properties.exists():
                    # --- 5. We found matches! Send the email. ---
                    self.stdout.write(self.style.SUCCESS(
                        f"Found {new_properties.count()} new properties for '{search.name}' (User: {user.username})"
                    ))

                    # 6. Prepare the email content
                    context = {
                        'user': user,
                        'search': search,
                        'new_properties': new_properties,
                        'new_properties_count': new_properties.count(),
                        'domain': DOMAIN, # Pass the domain to the template
                    }

                    # Render the HTML template we made in Step 4.2
                    html_message = render_to_string('accounts/email/saved_search_alert.html', context)
                    
                    # Also create a simple text-only version (good practice)
                    plain_message = f"Hi {user.username},\n\n"
                    plain_message += f"We found {new_properties.count()} new properties matching your saved search '{search.name}'.\n"
                    plain_message += f"Log in to http://{DOMAIN} to see them!\n\n- The PropWise Team"

                    # 7. Send the actual email
                    send_mail(
                        subject=f"PropWise Alert: {new_properties.count()} New Properties Match Your Search!",
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    
                    total_emails_sent += 1
                
                else:
                    # No new properties found for this search
                    self.stdout.write(
                        f"No new properties found for '{search.name}' (User: {user.username})."
                    )

                # --- 8. VERY IMPORTANT: Update the 'last_checked' time ---
                # This ensures we don't send the same alert twice.
                # We do this even if no properties were found.
                search.last_checked = timezone.now()
                search.save()

            except Exception as e:
                # Log any errors
                self.stderr.write(self.style.ERROR(
                    f"Error processing search {search.id} for user {user.username}: {e}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"[{timezone.now()}] Search alert process finished. Total emails sent: {total_emails_sent}"
        ))