package de.addiks.einsicht.abstract_syntax_tree.patterns;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

import java.util.*;

public class NodeBranch implements NodePattern {
    private final String grammarKey;
    private final Map<String, List<NodePattern>> patterns = new HashMap<>();

    public NodeBranch(String grammarKey, List<NodePattern> patterns) {
        this.grammarKey = grammarKey;
        for (NodePattern pattern : patterns) {
            this.patterns.computeIfAbsent(pattern.producedNodeKey(), k -> new ArrayList<>()).add(pattern);
        }
    }

    @Override
    public Set<String> consumedNodeKeys() {
        return patterns.keySet();
    }

    @Override
    public String producedNodeKey() {
        return grammarKey;
    }

    @Override
    public boolean matches(List<ASTNode> nodes, int index) {
        String grammarKey = nodes.get(index).grammarKey();
        if (patterns.containsKey(grammarKey)) {
            for (NodePattern pattern : patterns.get(grammarKey)) {
                if (pattern.producedNodeKey().equals(nodes.get(index).grammarKey())) {
                    return true;
                } else if (pattern.matches(nodes, index)) {
                    return true;
                }
            }
        }
        return false;
    }

    @Override
    public MutationResult mutate(List<ASTNode> nodes, int index) {
        String grammarKey = nodes.get(index).grammarKey();
        if (patterns.containsKey(grammarKey)) {
            for (NodePattern pattern : patterns.get(grammarKey)) {
                if (pattern.producedNodeKey().equals(nodes.get(index).grammarKey())) {
                    ASTNode replacedNode = nodes.get(index);
                    nodes.set(index, new ASTBranch(List.of(nodes.get(index)), grammarKey, null));
                    return new MutationResult(List.of(replacedNode), index);

                } else if (pattern.matches(nodes, index)) {
                    MutationResult innerResult = pattern.mutate(nodes, index);
                    nodes.set(innerResult.newIndex(), new ASTBranch(List.of(nodes.get(index)), grammarKey, null));
                    return innerResult;
                }
            }
        }

        return new MutationResult(List.of(), null);
    }
}
