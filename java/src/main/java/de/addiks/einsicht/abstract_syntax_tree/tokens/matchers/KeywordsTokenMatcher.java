package de.addiks.einsicht.abstract_syntax_tree.tokens.matchers;

import de.addiks.einsicht.abstract_syntax_tree.tokens.ConsumableString;
import de.addiks.einsicht.abstract_syntax_tree.tokens.TokenDef;
import de.addiks.einsicht.abstract_syntax_tree.tokens.TokenMatcher;
import de.addiks.einsicht.filehandling.codings.MappedString;

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
            MappedString code = text.substring(0, length);
            String check = code.asString();
            if (check.equalsIgnoreCase(keyword)) {
                token = new TokenDef("T_" + keyword.toUpperCase(), code, this);
                text.consume(length);
                break;
            }
        }
        return token;
    }
}
