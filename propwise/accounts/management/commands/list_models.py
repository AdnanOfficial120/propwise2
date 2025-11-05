# accounts/management/commands/list_models.py

import os
import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Lists all available Gemini models that support generateContent.'

    def handle(self, *args, **options):
        
        # 1. Configure the API key from your .env file
        try:
            genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
            self.stdout.write("Successfully configured API key.")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Could not configure API key: {e}"))
            return

        self.stdout.write("Connecting to Google AI to find available models...")
        
        try:
            # 2. This is the "Call ListModels" step
            found_models = []
            for m in genai.list_models():
                # We only care about models that can do what we want
                if 'generateContent' in m.supported_generation_methods:
                    found_models.append(m.name)

            # 3. Print the results
            if found_models:
                self.stdout.write(self.style.SUCCESS("--- Found Models ---"))
                for name in found_models:
                    self.stdout.write(name)
                self.stdout.write(self.style.SUCCESS("--------------------"))
                self.stdout.write(f"Please copy one of these model names (e.g., '{found_models[0]}')")
            else:
                self.stderr.write(self.style.ERROR("No models found that support 'generateContent'."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred while listing models: {e}"))