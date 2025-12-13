package de.addiks.einsicht.languages.tokens;

import java.util.concurrent.atomic.AtomicReference;

public abstract class TokenMatcher {
    abstract public TokenDef lexNext(ConsumableString text);
}
