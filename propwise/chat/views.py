from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse # Needed for notification links

# --- Local Imports ---
from .models import ChatThread, ChatMessage
from .forms import ChatMessageForm
from properties.models import Property

# --- Imports for our "Magic" Integrations ---
from accounts.models import Lead, LeadStatus, Notification

User = get_user_model()

@login_required(login_url='login')
def chat_inbox_view(request):
    """
    Display all active chat threads for the current user.
    """
    # We find all threads where the user is EITHER the buyer OR the agent.
    threads = ChatThread.objects.filter(
        Q(buyer=request.user) | Q(agent=request.user)
    ).order_by('-updated_at')

    context = {
        'threads': threads
    }
    return render(request, 'chat/inbox.html', context)


@login_required(login_url='login')
def start_chat_view(request, property_pk):
    """
    Finds or creates a chat thread for a given property and buyer.
    Triggers:
    1. Creates a new ChatThread (if needed).
    2. Creates a new Lead in the Agent's CRM.
    3. Sends a Notification to the Agent.
    """
    # We only accept POST requests to this view
    if request.method != 'POST':
        return HttpResponseForbidden()

    property = get_object_or_404(Property, pk=property_pk)
    agent = property.agent
    buyer = request.user

    # A user cannot start a chat with themselves
    if agent == buyer:
        return HttpResponseForbidden("You cannot start a chat with yourself.")

    # Find existing thread or create a new one
    thread, created = ChatThread.objects.get_or_create(
        property=property,
        buyer=buyer,
        agent=agent
    )
    
    # --- START: "MAGIC" AUTOMATION LOGIC ---
    # If this is a BRAND NEW thread ('created' is True), we trigger our business logic.
    if created:
        try:
            # 1. Create the Lead for the Agent's CRM
            Lead.objects.create(
                agent=agent,
                contact_name=buyer.get_full_name() or buyer.username,
                contact_email=buyer.email,
                contact_phone=buyer.phone_number,
                status=LeadStatus.NEW,
                source=f"PropWise Chat ({property.title})",
                property_of_interest=property,
                notes=f"New lead automatically generated from chat about {property.title}."
            )
            
            # 2. Create the Notification for the Agent
            Notification.objects.create(
                recipient=agent,
                message=f"New Lead! {buyer.username} started a chat about '{property.title}'.",
                link_url=reverse('my_leads') # Clicking takes them to their Lead Manager
            )
            
        except Exception as e:
            # If automation fails, log it but don't stop the chat
            print(f"Error in start_chat automation: {e}")
            
    # --- END: AUTOMATION LOGIC ---
    
    # Redirect the user to the chat room
    return redirect('chat_detail', thread_id=thread.id)


@login_required(login_url='login')
def chat_detail_view(request, thread_id):
    """
    Displays the chat room and handles sending new messages.
    Supports AJAX (JSON) responses for smoother chatting.
    """
    thread = get_object_or_404(ChatThread, id=thread_id)
    
    # Security check
    if request.user != thread.buyer and request.user != thread.agent:
        return HttpResponseForbidden("You do not have permission to view this chat.")

    # Mark messages as read when loading the page (GET request)
    if request.method == 'GET':
        thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # Handle Sending Messages (POST request)
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.save()
            
            # Update the thread's timestamp so it moves to the top of the inbox
            thread.save() 
            
            # Return JSON for JavaScript to handle
            return JsonResponse({"status": "success", "message": "Message sent!"})
        else:
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    
    # Load the page
    form = ChatMessageForm()
    context = {
        'thread': thread,
        'form': form
    }
    return render(request, 'chat/chat_detail.html', context)


@login_required(login_url='login')
def get_messages_api(request, thread_id):
    """
    An API view that returns all messages for a thread in JSON format.
    Used by JavaScript to refresh the chat without reloading the page.
    """
    thread = get_object_or_404(ChatThread, id=thread_id)
    
    # Security check
    if request.user != thread.buyer and request.user != thread.agent:
        return JsonResponse({"error": "Not authorized"}, status=403)
        
    # Mark messages as read
    thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # Build the list of messages
    message_list = []
    for message in thread.messages.all():
        message_list.append({
            'id': message.id,
            'sender_username': message.sender.username if message.sender else "Deleted User",
            'body': message.body,
            'timestamp': message.timestamp.strftime("%b %d, %Y, %I:%M %p"),
            'is_sender': message.sender == request.user
        })
    
    return JsonResponse({'messages': message_list})