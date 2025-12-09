package de.addiks.einsicht.languages.tokens;

import de.addiks.einsicht.languages.Language;

public class TokenDef {
    private final String tokenName;
    private final String code;
    private final TokenMatcher matcher;

    public TokenDef(String tokenName, String code, TokenMatcher matcher) {
        this.tokenName = tokenName;
        this.code = code;
        this.matcher = matcher;
    }

    public Token toToken(Language language, int row, int col, int offset) {
        return new Token(language, tokenName, code, row, col, offset);
    }

}
