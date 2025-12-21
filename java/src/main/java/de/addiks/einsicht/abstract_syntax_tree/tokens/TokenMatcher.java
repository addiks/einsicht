package de.addiks.einsicht.abstract_syntax_tree.tokens;

public abstract class TokenMatcher {
    abstract public TokenDef lexNext(ConsumableString text);
}
