package de.addiks.einsicht.semantics;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.selectors.ASTSelector;

public class FunctionHead implements Semantic.Local {
    private final ASTBranch node;
    private final String functionName;
    public FunctionHead(
            ASTBranch node,
            String functionName
    ) {
        this.node = node;
        this.functionName = functionName;
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
            return new FunctionHead(branch, ASTNode.reconstructCode(nameSelector.selectIn(branch)));
        }
    }
}
