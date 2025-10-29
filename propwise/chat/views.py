# chat/views.py

# chat/views.py
from django.shortcuts import render, get_object_or_404, redirect # Add redirect & get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ChatThread, ChatMessage # Import ChatMessage
from properties.models import Property # Import Property
from django.http import HttpResponseForbidden # To block bad requests
from .forms import ChatMessageForm


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


# ---    chat_detail_view  ---

@login_required(login_url='login')
def chat_detail_view(request, thread_id):
    """
    Displays the chat room and handles sending new messages.
    """
    thread = get_object_or_404(ChatThread, id=thread_id)

    # --- Security Check ---
    if request.user != thread.buyer and request.user != thread.agent:
        return HttpResponseForbidden("You do not have permission to view this chat.")

    # --- Mark Messages as Read ---
    thread.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # --- THIS IS THE NEW LOGIC FOR SENDING A MESSAGE ---
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            # Create the message object but don't save to DB yet
            message = form.save(commit=False)

            # Assign the correct thread and sender
            message.thread = thread
            message.sender = request.user
            message.save()

            # --- Professional Touch ---
            # Update the thread's 'updated_at' timestamp
            # This makes the inbox sort correctly (newest on top)
            thread.save() 

            # Redirect back to the same page to show the new message
            return redirect('chat_detail', thread_id=thread.id)
    else:
        # This is a GET request, so just show a blank form
        form = ChatMessageForm()

    # --- End of new logic ---

    context = {
        'thread': thread,
        'form': form  # <-- Pass the form into the template
    }

    return render(request, 'chat/chat_detail.html', context)