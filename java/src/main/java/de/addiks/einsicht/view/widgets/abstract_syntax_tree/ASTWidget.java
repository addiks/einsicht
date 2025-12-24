package de.addiks.einsicht.view.widgets.abstract_syntax_tree;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

public abstract class ASTWidget {
    private final ASTNode node;
    public ASTWidget(ASTNode node) {
        this.node = node;
    }

    abstract void addAstWidget(ASTWidget child);
}
