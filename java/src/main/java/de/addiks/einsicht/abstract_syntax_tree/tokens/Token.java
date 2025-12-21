package de.addiks.einsicht.abstract_syntax_tree.tokens;

import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.languages.Language;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

import java.util.List;

public class Token extends ASTNode {
    private final String tokenName;
    private final MappedString code;

    public Token(Language language, String tokenName, MappedString code, int row, int col, long offset) {
        super(language, row, col, offset, "token", null, List.of());
        this.code = code;
        this.tokenName = tokenName;
    }

    public String tokenName() {
        return tokenName;
    }

    @Override
    public MappedString.Builder newStringBuilder() {
        return code.newBuilder();
    }

    @Override
    public void reconstructCode(MappedString.Builder codeBuilder) {
        codeBuilder.append(code);
    }
}
