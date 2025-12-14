package de.addiks.einsicht.abstract_syntax_tree.patterns;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import org.jspecify.annotations.Nullable;

import java.util.List;
import java.util.Set;

public interface NodePattern {
    Set<String> consumedNodeKeys();
    String producedNodeKey();
    boolean matches(List<ASTNode> nodes, int index);
    MutationResult mutate(List<ASTNode> nodes, int index);

    record MutationResult(List<ASTNode> addedNodes, @Nullable Integer newIndex) {}
}
