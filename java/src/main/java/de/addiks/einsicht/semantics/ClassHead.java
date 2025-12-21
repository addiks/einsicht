package de.addiks.einsicht.semantics;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.selectors.ASTSelector;

public class ClassHead implements Semantic.Local {
    private ASTBranch node;
    private String localClassName;

    public ClassHead(
            ASTBranch node,
            String localClassName
    ) {
        this.node = node;
        this.localClassName = localClassName;
    }

    public String className() {
        return localClassName;
    }

    @Override
    public String name() {
        return "Class-Head " + localClassName;
    }

    @Override
    public ASTBranch node() {
        return node;
    }

    public static class Factory implements Semantic.Factory.Local {
        private final ASTSelector nameSelector;
        public Factory(ASTSelector nameSelector) {
            this.nameSelector = nameSelector;
        }

        @Override
        public Semantic.Local forBranch(ASTBranch branch) {
            return new ClassHead(
                    branch,
                    ASTNode.reconstructCode(
                            nameSelector.selectIn(branch),
                            branch.newStringBuilder()
                    )
            );
        }
    }
}
