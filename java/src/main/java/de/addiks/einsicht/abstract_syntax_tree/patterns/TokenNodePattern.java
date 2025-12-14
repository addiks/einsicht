package de.addiks.einsicht.abstract_syntax_tree.patterns;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.tokens.Token;

import java.util.List;
import java.util.Set;

public class TokenNodePattern implements NodePattern {
    private final String tokenName;

    public TokenNodePattern(String tokenName) {
        this.tokenName = tokenName;
    }

    @Override
    public Set<String> consumedNodeKeys() {
        return Set.of(tokenName);
    }

    @Override
    public String producedNodeKey() {
        return tokenName;
    }

    @Override
    public boolean matches(List<ASTNode> nodes, int index) {
        if (nodes.get(index) instanceof Token token) {
            return token.tokenName().equals(tokenName) || token.getCode().equals(tokenName);
        }
        return false;
    }

    @Override
    public MutationResult mutate(List<ASTNode> nodes, int index) {
        ASTNode node = nodes.get(index);
        assert node instanceof Token;
        Token token = (Token) node;
        assert tokenName.equals(token.tokenName()) || tokenName.equals(token.getCode());
        return new MutationResult(List.of(), index);
    }
}
