package de.addiks.einsicht.languages.tokens;

import de.addiks.einsicht.languages.Language;
import de.addiks.einsicht.languages.abstract_syntax_tree.ASTNode;

import java.util.List;

public class Token extends ASTNode {
    private final String tokenName;

    public Token(Language language, String tokenName, String code, int row, int col, int offset) {
        super(language, code, row, col, offset, "token", null, List.of());
        this.tokenName = tokenName;
    }

    public String tokenName() {
        return tokenName;
    }
}
