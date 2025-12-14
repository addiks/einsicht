package de.addiks.einsicht.tokens.matchers;

import de.addiks.einsicht.tokens.ConsumableString;
import de.addiks.einsicht.tokens.TokenDef;
import de.addiks.einsicht.tokens.TokenMatcher;

import java.util.List;

public class DirectTokenMatcher extends TokenMatcher {
    private final List<String> directTexts;
    private final String tokenName;

    public DirectTokenMatcher(String directText, String tokenName) {
        this(List.of(directText), tokenName);
    }

    public DirectTokenMatcher(List<String> directTexts, String tokenName) {
        this.directTexts = directTexts;
        this.tokenName = tokenName;
    }

    @Override
    public TokenDef lexNext(ConsumableString text) {
        for (String directText : directTexts) {
            if (text.startsWith(directText)) {
                return new TokenDef(tokenName, directText, this);
            }
        }
        return null;
    }
}
