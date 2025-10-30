# chat/views.py

# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect # Add redirect & get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ChatThread, ChatMessage # Import ChatMessage
from properties.models import Property # Import Property
from django.http import HttpResponseForbidden # To block bad requests
from .forms import ChatMessageForm
from django.http import JsonResponse


@login_required(login_url='login')
def chat_inbox_view(request):
    """
    Display all active chat threads for the current user.
    """

    # This is the professional way to query.
    # We find all threads where the user is EITHER the buyer OR the agent.
    threads = ChatThread.objects.filter(
        Q(buyer=request.user) | Q(agent=request.user)
    ).order_by('-updated_at') # Show newest active chats first

    context = {
        'threads': threads
    }

    return render(request, 'chat/inbox.html', context)





# ... your chat_inbox_view creating here... ...

@login_required(login_url='login')
def start_chat_view(request, property_pk):
    """
    Finds or creates a chat thread for a given property and buyer.
    This view is triggered by the "Contact Agent" button.
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

    # This is the professional way to do this:
    # get_or_create() attempts to find an object with these parameters.
    # If it exists, it "gets" it.
    # If not, it "creates" it and returns the new object.
    # This prevents duplicate chat threads.
    thread, created = ChatThread.objects.get_or_create(
        property=property,
        buyer=buyer,
        agent=agent
    )
    
    # Redirect the user to the chat room
    return redirect('chat_detail', thread_id=thread.id)


# ---    chat_detail_view  with live jason ---
# --- REPLACE your old chat_detail_view WITH THIS ---

@login_required(login_url='login')
def chat_detail_view(request, thread_id):
    """
    Displays the chat room and handles sending new messages.
    This view is now AJAX-aware.
    """
    thread = get_object_or_404(ChatThread, id=thread_id)
    
    if request.user != thread.buyer and request.user != thread.agent:
        return HttpResponseForbidden("You do not have permission to view this chat.")

    # Mark messages as read (only on GET, when the page *loads*)
    if request.method == 'GET':
        thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # --- THIS IS THE UPDATED LOGIC FOR SENDING ---
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender = request.user
            message.save()
            
            # Update the thread's 'updated_at' timestamp
            thread.save() 
            
            # --- PROFESSIONAL FIX ---
            # Instead of redirecting, we return a simple JSON response.
            # Our JavaScript will catch this and know the message was sent.
            return JsonResponse({"status": "success", "message": "Message sent!"})
        else:
            # If the form is invalid (e.g., empty message)
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
    
    # --- This is for the GET request (loading the page) ---
    form = ChatMessageForm()
    
    context = {
        'thread': thread,
        'form': form
    }
    
    return render(request, 'chat/chat_detail.html', context)



# --- ADD THIS NEW VIEW to make chat app reload , live ---

@login_required(login_url='login')
def get_messages_api(request, thread_id):
    """
    An "API" view that returns all messages for a
    chat thread in JSON format.
    """
    thread = get_object_or_404(ChatThread, id=thread_id)
    
    # Security check: User must be part of this thread
    if request.user != thread.buyer and request.user != thread.agent:
        return JsonResponse({"error": "Not authorized"}, status=403)
        
    # Mark messages as read (we'll keep this logic)
    thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # Convert the messages into a list of "safe" dictionaries
    message_list = []
    for message in thread.messages.all():
        message_list.append({
            'id': message.id,
            'sender_username': message.sender.username if message.sender else "Deleted User",
            'body': message.body,
            'timestamp': message.timestamp.strftime("%b %d, %Y, %I:%M %p"), # "Oct 30, 2025, 11:30 AM"
            'is_sender': message.sender == request.user # True if the current user sent it
        })
    
    # Return the list as a JSON object
    return JsonResponse({'messages': message_list})