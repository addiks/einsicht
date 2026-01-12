package de.addiks.einsicht;

import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.annotation.*;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Hub
{
    private static final Logger log = LoggerFactory.getLogger(Hub.class);
    private final Map<Class<?>,Object> objects = new HashMap<>();
    private final Map<Method, List<Listener>> methodListeners = new HashMap<>();
    private final Map<Class<?>, List<Listener>> classListeners = new HashMap<>();

    public Hub ()
    {
        
    }

    public static Hub instance() {
        return Application.instance().hub();
    }

    public void register(Object target) {
        register(target, target.getClass());
    }

    public <T> void register(T target, Class<? extends T> key) {
        log.debug("Hub registered {} as {}", target, key);
        objects.put(key, target);
        Class<?> superClass = key.getSuperclass();
        if (superClass != null && superClass != Object.class) {
            register(target, superClass);
        }
        for (Class<?> interfaceClass : key.getInterfaces()) {
            register(target, interfaceClass);
        }
        notify(key);
    }

    public <T> @NullMarked T get(Class<T> target) {
        if (objects.containsKey(target)) {
            return (T) objects.get(target);
        }
        return null;
    }

    public boolean has(Class<?> target) {
        return objects.containsKey(target);
    }

    public void remove(Class<?> target) {
        objects.remove(target);
    }

    public void on(Class<?> event, Listener listener) {
        log.debug("Hub listening on {} for handler {}", event, listener);
        classListeners.computeIfAbsent(event, k -> new ArrayList<>()).add(listener);
    }

    public void on(Method event, Listener listener) {
        log.debug("Hub listening on {} for handler {}", event, listener);
        methodListeners.computeIfAbsent(event, k -> new ArrayList<>()).add(listener);
    }

    public void notify(Class<?> subject, Object... arguments) {
        if (classListeners.containsKey(subject)) {
            for (Listener listener : classListeners.get(subject)) {
                listener.apply(arguments);
            }
        }
    }

    public void notify(Method subject, Object... arguments) {
        if (methodListeners.containsKey(subject)) {
            for (Listener listener : methodListeners.get(subject)) {
                listener.apply(arguments);
            }
        }
    }

    public void notify(Class<?> clazz, String method) {
        try {
            notify(clazz, clazz.getMethod(method));
        } catch (NoSuchMethodException e) {
            log.error("Cannot notify {}::{} because {}", clazz.getName(), method, e.getMessage(), e);
            throw new RuntimeException(e);
        }
    }

    public void setup(Object subject) {
        register(subject);
        for (Method method : subject.getClass().getMethods()) {
            if (method.isAnnotationPresent(On.class)) {
                this.on(method, (args) -> {
                    try {
                        method.invoke(subject, args);
                    } catch (IllegalAccessException | InvocationTargetException e) {
                        throw new RuntimeException(e);
                    }
                });
            }
        }
    }

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    public @interface On {
    }

    @FunctionalInterface
    public interface Listener {
        void apply(Object... args);
    }

}
