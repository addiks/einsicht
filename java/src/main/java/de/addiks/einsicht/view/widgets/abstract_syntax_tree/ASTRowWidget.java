package de.addiks.einsicht.view.widgets.abstract_syntax_tree;

public class ASTRowWidget {
    private final ASTRowWidgetContainer container;
    private final int lineNumber;
    public ASTRowWidget(ASTRowWidgetContainer container, int lineNumber) {
        this.container = container;
        this.lineNumber = lineNumber;
    }

    public void addAstWidget(ASTWidget child) {

    }
}
