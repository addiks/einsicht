package de.addiks.einsicht.languages.tokens.matchers;

import de.addiks.einsicht.languages.tokens.ConsumableString;
import de.addiks.einsicht.languages.tokens.Token;
import de.addiks.einsicht.languages.tokens.TokenDef;
import de.addiks.einsicht.languages.tokens.TokenMatcher;

import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

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
