package de.addiks.einsicht.abstract_syntax_tree.tokens;

public abstract class MutatingTokenMatcher extends TokenMatcher {
    abstract public Token mutateToken(Token token, String newCode);
}
