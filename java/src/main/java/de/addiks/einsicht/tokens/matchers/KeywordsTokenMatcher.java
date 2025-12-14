package de.addiks.einsicht.tokens.matchers;

import de.addiks.einsicht.tokens.ConsumableString;
import de.addiks.einsicht.tokens.TokenDef;
import de.addiks.einsicht.tokens.TokenMatcher;

import java.util.List;

public class KeywordsTokenMatcher extends TokenMatcher {
    private final List<String> keywords;

    public KeywordsTokenMatcher(List<String> keywords) {
        this.keywords = keywords;
    }

    @Override
    public TokenDef lexNext(ConsumableString text) {
        TokenDef token = null;
        for (String keyword : keywords) {
            int length = keyword.length();
            String check = text.substring(0, length);
            if (check.equalsIgnoreCase(keyword)) {
                token = new TokenDef("T_" + keyword.toUpperCase(), keyword, this);
                text.consume(length);
                break;
            }
        }
        return token;
    }
}
