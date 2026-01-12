package de.addiks.einsicht.abstract_syntax_tree.selectors;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

public class ParentSelector implements ASTSelector {
    private final ASTSelector defered;
    public ParentSelector(ASTSelector defered) {
        this.defered = defered;
    }

    @Override
    public boolean matches(ASTNode node) {
        ASTNode parent = node.parent();
        if (parent == null) {
            return false;
        }
        return defered.matches(parent);
    }
}
