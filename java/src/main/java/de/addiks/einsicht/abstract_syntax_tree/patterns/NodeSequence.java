package de.addiks.einsicht.abstract_syntax_tree.patterns;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;

public class NodeSequence implements NodePattern {
    private final List<NodePattern> elements;
    private final String grammarKey;

    public NodeSequence(String grammarKey, List<NodePattern> elements) {
        assert !elements.isEmpty();
        this.elements = elements;
        this.grammarKey = grammarKey;
    }

    @Override
    public Set<String> consumedNodeKeys() {
        return Set.of(elements.getFirst().producedNodeKey());
    }

    @Override
    public String producedNodeKey() {
        return grammarKey;
    }

    @Override
    public boolean matches(List<ASTNode> nodes, int index) {
        nodes = new ArrayList<>(nodes);
        for (NodePattern pattern : elements) {
            if (nodes.size() <= index) {
                break;
            }
            if (pattern.matches(nodes, index)) {
                MutationResult result = pattern.mutate(nodes, index);
                if (result.newIndex() != null) {
                    index = result.newIndex() + 1;
                }
            } else if (pattern.producedNodeKey().equals(nodes.get(index).grammarKey())) {
                index++;
            } else {
                return false;
            }
        }
        return true;
    }

    @Override
    public MutationResult mutate(List<ASTNode> nodes, int index) {
        List<ASTNode> allNewNodes = new ArrayList<>();
        List<ASTNode> allReplacedNodes = new ArrayList<>();
        int start = index;
        int end = index;

        for (NodePattern pattern : elements) {
            if (nodes.size() <= index) {
                break;
            }
            if (pattern.matches(nodes, index)) {
                MutationResult patternResult = pattern.mutate(nodes, index);
                if (patternResult.newIndex() != null) {
                    allNewNodes.add(nodes.get(patternResult.newIndex()));
                    allReplacedNodes.addAll(patternResult.addedNodes());
                    start = Math.min(start, patternResult.newIndex());
                    end = Math.max(end, patternResult.newIndex());
                    index = patternResult.newIndex() + 1;
                }
            } else if (pattern.producedNodeKey().equals(nodes.get(index).grammarKey())) {
                allNewNodes.add(nodes.get(index));
                start = Math.min(start, index);
                end = Math.max(end, index);
                index++;
            }
        }

        for (int subIndex = end + 1; subIndex >= start + 1; subIndex--) {
            nodes.remove(subIndex);
        }

        nodes.set(start, new ASTBranch(allNewNodes, grammarKey, null));

        return new MutationResult(allReplacedNodes, start);
    }
}
