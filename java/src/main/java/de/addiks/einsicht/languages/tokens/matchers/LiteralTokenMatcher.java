package de.addiks.einsicht.languages.tokens.matchers;

import de.addiks.einsicht.languages.tokens.ConsumableString;
import de.addiks.einsicht.languages.tokens.TokenDef;
import de.addiks.einsicht.languages.tokens.TokenMatcher;

import java.util.concurrent.atomic.AtomicReference;

public class LiteralTokenMatcher extends TokenMatcher {
    private final char delimitter;
    private final String tokenName;

    public LiteralTokenMatcher(char delimitter, String tokenName) {
        this.delimitter = delimitter;
        this.tokenName = tokenName;
    }

    @Override
    public TokenDef lexNext(ConsumableString text) {
        TokenDef token = null;
        if (text.charAt(0) == delimitter) {
            boolean end = false;
            int index = 0;
            while (!end) {
                index++;
                if (index >= text.length() || text.charAt(0) == delimitter) {
                    end = true;
                }
            }
            token = new TokenDef(tokenName, text.consume(index + 1), this);
        }
        return token;
    }
}
