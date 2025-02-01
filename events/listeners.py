activity_listeners = []

def listen_for_events(model):
    """Registers a model to trigger event progress updates."""
    activity_listeners.append(model)