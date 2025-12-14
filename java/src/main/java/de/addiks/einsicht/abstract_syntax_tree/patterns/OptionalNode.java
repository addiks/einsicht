package de.addiks.einsicht.abstract_syntax_tree.patterns;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

import java.util.List;
import java.util.Set;

public class OptionalNode implements NodePattern {
    private final NodePattern pattern;

    public OptionalNode(
            NodePattern pattern
    ) {
        this.pattern = pattern;
    }

    @Override
    public boolean matches(List<ASTNode> nodes, int index) {
        return true;
    }

    @Override
    public Set<String> consumedNodeKeys() {
        return pattern.consumedNodeKeys();
    }

    @Override
    public String producedNodeKey() {
        return pattern.producedNodeKey();
    }

    @Override
    public MutationResult mutate(List<ASTNode> nodes, int index) {
        if (pattern.matches(nodes, index)) {
            return pattern.mutate(nodes, index);
        }
        return new MutationResult(List.of(), null);
    }
}
