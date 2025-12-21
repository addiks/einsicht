package de.addiks.einsicht.abstract_syntax_tree.tokens;

import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.languages.Language;

public class TokenDef {
    private final String tokenName;
    private final MappedString code;
    private final TokenMatcher matcher;

    public TokenDef(String tokenName, MappedString code, TokenMatcher matcher) {
        this.tokenName = tokenName;
        this.code = code;
        this.matcher = matcher;
    }

    public Token toToken(Language language, int row, int col, long offset) {
        return new Token(language, tokenName, code, row, col, offset);
    }

}
