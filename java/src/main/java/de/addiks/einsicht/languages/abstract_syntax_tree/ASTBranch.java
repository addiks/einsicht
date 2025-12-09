package de.addiks.einsicht.languages.abstract_syntax_tree;

import de.addiks.einsicht.languages.Language;
import org.jspecify.annotations.Nullable;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ASTBranch extends ASTNode {
    private final Map<ASTNode, Integer> childToIndex;

    public ASTBranch(
            List<ASTNode> children,
            String grammarKey,
            @Nullable ASTBranch parent
    ) {
        super(children.getFirst(), codeOf(children), grammarKey, parent, children);
        childToIndex = new HashMap<>();
        int index = 0;
        for (ASTNode child : children) {
            childToIndex.put(child, index);
            index++;
        }
    }

    private static String codeOf(List<ASTNode> nodes) {
        StringBuilder code = new StringBuilder();
        for (ASTNode child : nodes) {
            child.reconstructCode(code);
        }
        return code.toString();
    }

    @Override
    public @Nullable ASTNode nextChild(ASTNode previous) {
        if (childToIndex.containsKey(previous)) {
            int index = childToIndex.get(previous) + 1;
            if (index < childToIndex.size()) {
                return child(index);
            }
        }
        return null;
    }

    @Override
    public @Nullable ASTNode previousChild(ASTNode next) {
        if (childToIndex.containsKey(next)) {
            int index = childToIndex.get(next) - 1;
            if (index >= 0) {
                return child(index);
            }
        }
        return null;
    }
}
