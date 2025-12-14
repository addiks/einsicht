package de.addiks.einsicht.abstract_syntax_tree;

import de.addiks.einsicht.semantics.Semantic;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ASTBranch extends ASTNode {
    private final Map<ASTNode, Integer> childToIndex;
    private final Map<Class<? extends Semantic>, Semantic> semantics = new HashMap<>();

    public ASTBranch(
            List<ASTNode> children,
            String grammarKey
    ) {
        this(children, grammarKey, null);
    }

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

    public List<Semantic> semantics() {
        return new ArrayList<>(semantics.values());
    }

    public boolean hasSemantic(Class<Semantic> semanticClass) {
        return semantics.containsKey(semanticClass);
    }

    public Semantic semantic(Class<Semantic> semanticClass) {
        return semantics.get(semanticClass);
    }

    public void assignSemantic(Semantic semantic) {
        assert !semantics.containsKey(semantic.getClass());
        semantics.put(semantic.getClass(), semantic);
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

    private static String codeOf(List<ASTNode> nodes) {
        StringBuilder code = new StringBuilder();
        for (ASTNode child : nodes) {
            child.reconstructCode(code);
        }
        return code.toString();
    }

}
