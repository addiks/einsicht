package de.addiks.einsicht.semantics;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.selectors.ASTSelector;

public class VariableDeclaration implements Semantic.Local {
    private final ASTBranch node;
    private final String variableName;
    public VariableDeclaration(
            ASTBranch node,
            String variableName
    ) {
        this.node = node;
        this.variableName = variableName;
    }

    @Override
    public ASTBranch node() {
        return node;
    }

    @Override
    public String name() {
        return "";
    }

    public static class Factory implements Semantic.Factory.Local {
        private final ASTSelector nameSelector;
        public Factory(ASTSelector nameSelector) {
            this.nameSelector = nameSelector;
        }

        @Override
        public Semantic.Local forBranch(ASTBranch branch) {
            return new VariableDeclaration(branch, ASTNode.reconstructCode(
                    nameSelector.selectIn(branch),
                    branch.newStringBuilder()
            ));
        }
    }
}
