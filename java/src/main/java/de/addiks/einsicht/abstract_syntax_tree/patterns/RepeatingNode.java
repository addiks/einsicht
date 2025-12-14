package de.addiks.einsicht.abstract_syntax_tree.patterns;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

import java.util.List;
import java.util.Set;

public class RepeatingNode implements NodePattern {
    private final NodePattern pattern;
    private final boolean optional;
    private final String grammarKey;

    public RepeatingNode(String grammarKey, NodePattern pattern, boolean optional) {
        this.pattern = pattern;
        this.optional = optional;
        this.grammarKey = grammarKey;
    }

    @Override
    public Set<String> consumedNodeKeys() {
        return pattern.consumedNodeKeys();
    }

    @Override
    public String producedNodeKey() {
        return grammarKey;
    }

    @Override
    public boolean matches(List<ASTNode> nodes, int index) {
        if (optional) {
            return true;
        } else {
            return pattern.matches(nodes, index);
        }
    }

    @Override
    public MutationResult mutate(List<ASTNode> nodes, int index) {
        List<ASTNode> allReplacedNodes = List.of();
        List<ASTNode> allNewNodes = List.of();
        Integer start = index;
        int end = index;

        Set<String> nodeKeys = consumedNodeKeys();
        while (true) {
            if (nodes.size() <= index) {
                break;
            }
            if (pattern.matches(nodes, index)) {
                MutationResult result = pattern.mutate(nodes, index);

                start = Math.min(start, result.newIndex());
                end = Math.max(end, result.newIndex());

                allReplacedNodes.addAll(result.addedNodes());
                allNewNodes.add(nodes.get(result.newIndex()));

                index = result.newIndex() + 1;

            } else if (nodes.get(index).getGrammarKey().equals(pattern.producedNodeKey())) {
                index++;

            } else {
                break;
            }
        }

        for (int subIndex = end + 1; subIndex >= start + 1; subIndex--) {
            nodes.remove(subIndex);
        }

        if (!allNewNodes.isEmpty()) {
            nodes.set(start, new ASTBranch(allNewNodes, grammarKey, null));
        } else {
            start = null;
        }

        return new MutationResult(allReplacedNodes, start);
    }
}
