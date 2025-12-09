package de.addiks.passwordtrainer;

import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.function.Consumer;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

public class EventDispatcher {
    private static final Logger LOGGER = LogManager.getLogger();

    private final Map<Class<?>, List<Consumer<Event>>> listeners = new HashMap<>();    
    private final List<Consumer<Event>> allListeners = new ArrayList<>();

    public void subscribe(Consumer<Event> listener, Class<?> target) {
        if (!listeners.containsKey(target)) {
            listeners.put(target, new ArrayList<>());
        }
        listeners.get(target).add(listener);
    }
   
    public void subscribeToAll(Consumer<Event> listener) {
        allListeners.add(listener);
    }
    
    public void dispatch(Event event) {
        Class<?> clazz = event.getClass();
        if (listeners.containsKey(clazz)) {
            listeners.get(clazz).forEach(l -> l.accept(event));
        }
        allListeners.forEach(l -> l.accept(event));
    }
    
}
