package de.addiks.einsicht.abstract_syntax_tree;

import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.semantics.Semantic;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ASTBranch extends ASTNode {
    private final Map<ASTNode, Integer> childToIndex;
    private final Map<Class<? extends Semantic>, Semantic> semantics = new HashMap<>();

    public ASTBranch(List<ASTNode> children, String grammarKey) {
        this(children, grammarKey, null);
    }

    public ASTBranch(
            List<ASTNode> children,
            String grammarKey,
            @Nullable ASTBranch parent
    ) {
        super(children.getFirst(), grammarKey, parent, children);
        childToIndex = new HashMap<>();
        int index = 0;
        for (ASTNode child : children) {
            child.setParent(this);
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
    public void collectTokens(List<Token> tokens) {
        for (ASTNode prepended : getPrepended()) {
            tokens.addAll(prepended.collectTokens());
        }
        for (ASTNode child : children) {
            tokens.addAll(child.collectTokens());
        }
        for (ASTNode appended : getAppended()) {
            tokens.addAll(appended.collectTokens());
        }
    }

    @Override
    public MappedString.Builder newStringBuilder() {
        return firstToken().newStringBuilder();
    }

    @Override
    public void reconstructCode(MappedString.Builder codeBuilder) {
        for (ASTNode prepended : getPrepended()) {
            prepended.reconstructCode(codeBuilder);
        }
        for (ASTNode child : getChildren()) {
            child.reconstructCode(codeBuilder);
        }
        for (ASTNode appended : getAppended()) {
            appended.reconstructCode(codeBuilder);
        }
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

    public @Nullable Token firstToken() {
        ASTNode first = firstChild();
        if (first instanceof Token token) {
            return token;
        } else if (first instanceof ASTBranch firstBranch) {
            return firstBranch.firstToken();
        }
        return null;
    }

    public @Nullable Token lastToken() {
        ASTNode last = lastChild();
        if (last instanceof Token token) {
            return token;
        } else if (last instanceof ASTBranch lastBranch) {
            return lastBranch.lastToken();
        }
        return null;
    }

}
