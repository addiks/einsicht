package de.addiks.einsicht.abstract_syntax_tree.selectors;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

public class AlwaysTrue implements ASTSelector {
    @Override
    public boolean matches(ASTNode node) {
        return true;
    }
}
