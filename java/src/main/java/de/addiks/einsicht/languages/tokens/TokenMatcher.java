package de.addiks.einsicht.languages.tokens;

import java.util.concurrent.atomic.AtomicReference;

public abstract class TokenMatcher {
    abstract public TokenDef lexNext(AtomicReference<String> text);

    abstract public Token mutateToken(Token token, String newCode);
}
