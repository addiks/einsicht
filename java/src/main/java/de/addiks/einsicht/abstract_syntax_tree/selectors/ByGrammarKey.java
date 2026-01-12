package de.addiks.einsicht.abstract_syntax_tree.selectors;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

public class ByGrammarKey implements ASTSelector {
    private final String grammarKey;
    public ByGrammarKey(String grammarKey) {
        this.grammarKey = grammarKey;
    }

    @Override
    public boolean matches(ASTNode node) {
        return node.grammarKey().equalsIgnoreCase(grammarKey);
    }
}
