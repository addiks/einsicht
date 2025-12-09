package de.addiks.einsicht.languages.abstract_syntax_tree.patterns;

import de.addiks.einsicht.languages.abstract_syntax_tree.ASTNode;
import org.jspecify.annotations.Nullable;

import java.util.List;
import java.util.Set;

public class LateDefinedASTPattern implements NodePattern {
    private @Nullable NodePattern pattern = null;
    private @Nullable final String producedNodeKey;

    public LateDefinedASTPattern(@Nullable String producedNodeKey) {
        this.producedNodeKey = producedNodeKey;
    }

    public void definePattern(NodePattern pattern) {
        this.pattern = pattern;
    }

    @Override
    public Set<String> consumedNodeKeys() {
        assert pattern != null;
        return pattern.consumedNodeKeys();
    }

    @Override
    public String producedNodeKey() {
        if (producedNodeKey != null) {
            return producedNodeKey;
        }
        assert pattern != null;
        return pattern.producedNodeKey();
    }

    @Override
    public boolean matches(List<ASTNode> nodes, int index) {
        assert pattern != null;
        return pattern.matches(nodes, index);
    }

    @Override
    public MutationResult mutate(List<ASTNode> nodes, int index) {
        assert pattern != null;
        return pattern.mutate(nodes, index);
    }
}
