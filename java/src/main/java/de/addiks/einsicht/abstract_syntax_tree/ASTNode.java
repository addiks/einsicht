package de.addiks.einsicht.abstract_syntax_tree;

import de.addiks.einsicht.abstract_syntax_tree.selectors.ASTSelector;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import de.addiks.einsicht.filehandling.codings.DecodedCharacter;
import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.languages.Language;
import org.apache.commons.lang3.StringUtils;
import org.jspecify.annotations.NonNull;
import org.jspecify.annotations.Nullable;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Predicate;


public abstract class ASTNode {
    private final Language language;
    private boolean dirty = false;
    private final int row;
    private @Nullable Integer lastRow = null;
    private final int col;
    private final long offset;
    private final String grammarKey;
    private @Nullable ASTBranch parent;
    protected final List<ASTNode> children = new ArrayList<>();
    private final Map<String, String> attributes = new HashMap<>();
    private final List<ASTNode> prepended = new ArrayList<>();
    private final List<ASTNode> appended = new ArrayList<>();

    public ASTNode(
            Language language,
            int row,
            int col,
            int offset,
            String grammarKey
    ) {
        this(language, row, col, offset, grammarKey, null, List.of());
    }

    public ASTNode(
            Language language,
            int row,
            int col,
            long offset,
            String grammarKey,
            @Nullable ASTBranch parent,
            List<ASTNode> children
    ) {
        this.language = language;
        this.row = row;
        this.col = col;
        this.offset = offset;
        this.grammarKey = grammarKey;
        this.parent = parent;
        this.children.addAll(children);
    }

    protected ASTNode(
        ASTNode example,
        String grammarKey,
        @Nullable ASTBranch parent,
        List<ASTNode> children
    ) {
        this(
                example.getLanguage(),
                example.getRow(),
                example.getCol(),
                example.getOffset(),
                grammarKey,
                parent,
                children
        );
    }

    public Path filePath() {
        return parent.filePath();
    }

    public int lastRow() {
        if (lastRow == null) {
            lastRow = row + getCode().substringCount("\n");
        }
        return lastRow;
    }

    public void prepend(ASTNode node) {
        prepended.add(node);
    }

    public void append(ASTNode node) {
        appended.add(node);
    }

    public List<Token> collectTokens() {
        List<Token> tokens = new ArrayList<>();
        collectTokens(tokens);
        return tokens;
    }

    public abstract void collectTokens(List<Token> tokens);

    public abstract MappedString.Builder newStringBuilder();

    public MappedString reconstructCode() {
        MappedString.Builder builder = newStringBuilder();
        reconstructCode(builder);
        return builder.build();
    }

    public abstract void reconstructCode(MappedString.Builder codeBuilder);

    public static String reconstructCode(List<ASTNode> nodes, MappedString.Builder codeBuilder) {
        for (ASTNode node : nodes) {
            node.reconstructCode(codeBuilder);
        }
        return codeBuilder.toString();
    }

    public boolean isDirty() {
        return dirty;
    }

    public ASTNode child(int index) {
        return children.get(index);
    }

    public boolean matches(Selector selector) {
        return selector.matches(this);
    }

    public List<ASTNode> find(Selector selector) {
        List<ASTNode> result = new ArrayList<>();
        for (ASTNode child : children) {
            result.addAll(child.find(selector));
        }
        if (matches(selector)) {
            result.add(this);
        }
        return result;
    }

    public List<ASTNode> findInPrepended(Selector selector) {
        List<ASTNode> result = new ArrayList<>();
        if (!children.isEmpty()) {
            result.addAll(children.getFirst().findInPrepended(selector));
        }
        for (ASTNode child : prepended) {
            result.addAll(child.find(selector));
        }
        if (matches(selector)) {
            result.add(this);
        }
        return result;
    }

    public List<ASTNode> findInAppended(Selector selector) {
        List<ASTNode> result = new ArrayList<>();
        if (!children.isEmpty()) {
            result.addAll(children.getLast().findInAppended(selector));
        }
        for (ASTNode child : appended) {
            result.addAll(child.find(selector));
        }
        if (matches(selector)) {
            result.add(this);
        }
        return result;
    }

    public @Nullable ASTNode findAtOffset(int offset) {
        for (ASTNode child : children) {
            if (child.isAtOffset(offset)) {
                return child.findAtOffset(offset);
            }
        }
        if (isAtOffset(offset)) {
            return this;
        }
        return null;
    }

    public boolean isAtOffset(int offset) {
        if (this.offset > offset) {
            return false;
        }
        return this.offset + getCode().length() > offset;
    }

    public boolean hasParentWith(Selector selector) {
        if (parent != null) {
            return parent.matches(selector) && parent.hasParentWith(selector);
        }
        return false;
    }

    public @Nullable Integer offsetIn(List<ASTNode> nodes) {
        if (!nodes.contains(this)) {
            return null;
        }
        return nodes.indexOf(this);
    }

    public String grammarKey() {
        return grammarKey;
    }

    public @Nullable ASTNode next() {
        if (parent != null) {
            return parent.nextChild(this);
        }
        return null;
    }

    public @Nullable ASTNode previous() {
        if (parent != null) {
            return parent.previousChild(this);
        }
        return null;
    }

    public @Nullable ASTNode nextChild(ASTNode previous) {
        return null;
    }

    public @Nullable ASTNode previousChild(ASTNode next) {
        return null;
    }

    public @Nullable ASTNode firstChild() {
        if (!prepended.isEmpty()) {
            return prepended.getFirst();
        } else if (!children.isEmpty()) {
            return children.getFirst();
        }
        return null;
    }

    public @Nullable ASTNode lastChild() {
        if (!appended.isEmpty()) {
            return appended.getLast();
        } else if (!children.isEmpty()) {
            return children.getLast();
        }
        return null;
    }

    public Language getLanguage() {
        return language;
    }

    public MappedString getCode() {
        // TODO: Some caching here?
        return reconstructCode();
    }

    public int getRow() {
        return row;
    }

    public @Nullable Integer getLastRow() {
        return lastRow;
    }

    public int getCol() {
        return col;
    }

    public long getOffset() {
        return offset;
    }

    public String getGrammarKey() {
        return grammarKey;
    }

    public @Nullable ASTNode getParent() {
        return parent;
    }

    public void setParent(@Nullable ASTBranch parent) {
        this.parent = parent;
    }

    public List<ASTNode> getChildren() {
        return children;
    }

    public Map<String, String> getAttributes() {
        return attributes;
    }

    public List<ASTNode> getPrepended() {
        return prepended;
    }

    public List<ASTNode> getAppended() {
        return appended;
    }

    public void iterate(Consumer<ASTNode> consumer) {
        for (ASTNode predecessor : prepended) {
            predecessor.iterate(consumer);
        }
        consumer.accept(this);
        for (ASTNode child : children) {
            child.iterate(consumer);
        }
        for (ASTNode successor : appended) {
            successor.iterate(consumer);
        }
    }

    public static class Selector implements ASTSelector {
        private @Nullable String grammarKey;
        private @Nullable Predicate<ASTNode> predicate;

        public Selector(@NonNull String grammarKey) {
            this.grammarKey = grammarKey;
        }

        public Selector(@NonNull Predicate<ASTNode> predicate) {
            this.predicate = predicate;
        }

        public boolean matches(ASTNode node) {
            if (grammarKey != null && grammarKey.equals(node.grammarKey())) {
                return true;
            }
            return predicate != null && predicate.test(node);
        }
    }

}
