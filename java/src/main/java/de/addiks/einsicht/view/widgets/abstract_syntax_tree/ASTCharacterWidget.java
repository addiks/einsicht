package de.addiks.einsicht.view.widgets.abstract_syntax_tree;

public class ASTCharacterWidget {
    private final ASTTokenWidget parent;
    private final char character;

    public ASTCharacterWidget(ASTTokenWidget parent, char character) {
        this.parent = parent;
        this.character = character;
    }
}
