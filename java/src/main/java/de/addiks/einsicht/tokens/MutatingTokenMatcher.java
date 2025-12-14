package de.addiks.einsicht.tokens;

public abstract class MutatingTokenMatcher extends TokenMatcher {
    abstract public Token mutateToken(Token token, String newCode);
}
