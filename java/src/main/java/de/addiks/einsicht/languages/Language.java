package de.addiks.einsicht.languages;

import de.addiks.einsicht.Hub;
import de.addiks.einsicht.languages.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.languages.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.languages.abstract_syntax_tree.patterns.NodeBranch;
import de.addiks.einsicht.languages.abstract_syntax_tree.patterns.NodePattern;
import de.addiks.einsicht.languages.tokens.Token;
import de.addiks.einsicht.languages.tokens.TokenDef;
import de.addiks.einsicht.languages.tokens.TokenMatcher;
import org.apache.commons.lang3.StringUtils;
import org.jspecify.annotations.Nullable;

import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

public abstract class Language {
    private static final MessageDigest md5;
    static {
        try {
            md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    private final Map<String, List<Token>> lexCache = new HashMap<>();
    private final Map<String, ParseResult> parseCache = new HashMap<>();
    private final Hub hub;
    private Map<String,List<NodePattern>> grammarMap = null;

    public Language(Hub hub) {
        this.hub = hub;
        hub.register(this);
    }

    public abstract String name();

    public boolean debugEnabled() {
        return false;
    }

    public abstract List<TokenMatcher> tokenMatchers();

    public abstract List<NodePattern> grammar();

    public List<ASTNode> groupStatementsIntoBlocks(List<ASTNode> nodes) {
        return nodes;
    }

    public abstract Object stylesheet();

    public abstract boolean isNodeRelevantForGrammar(ASTNode node);

    public ParseResult parse(String code, Path filepath, @Nullable ASTRoot previousAST, @Nullable List<Token> previousTokens) {
        String hash = new String(md5.digest(code.getBytes(StandardCharsets.UTF_8)));
        if (!parseCache.containsKey(hash)) {
            List<Token> tokens = lex(code, previousTokens);
            if (tokens.size() > 0) {
                List<NodePattern> grammar = grammar();

                tokens = normalize(tokens);

                List<ASTNode> nodes = applyGrammar(tokens, grammar);
                nodes = groupStatementsIntoBlocks(nodes);

                if (debugEnabled()) {
                    dumpAST(nodes);
                }

                ASTRoot ast = new ASTRoot(nodes, filepath);
                hub.register(ast);

                parseCache.put(hash, new ParseResult(ast, tokens));
            }
        }
        return parseCache.getOrDefault(hash, new ParseResult(null, tokens));
    }

    public record ParseResult(
            @Nullable ASTRoot previousAST,
            List<Token> previousTokens
    ) {}

    public List<ASTNode> applyGrammar(List<Token> nodes, List<NodePattern> grammar) {
        Map<String, List<ASTNode>> nodeMap = mapNodes(nodes);
        while (!nodeMap.isEmpty()) {
            boolean hasMutated = false;
            for (String key : nodeMap.keySet()) {

            }
        }
    }

    private Map<String, List<Token>> mapNodes(List<Token> nodes) {
        Map<String, List<Token>> nodeMap = new HashMap<>();
        for (int index = 0; index < nodes.size(); index++) {
            Token token = nodes.get(index);
            nodeMap.computeIfAbsent(token.tokenName(), t -> new ArrayList<>()).add(token);
            nodeMap.computeIfAbsent(token.getCode(), t -> new ArrayList<>()).add(token);
        }
        return nodeMap;
    }

    private List<ASTNode> normalize(List<ASTNode> nodes) {
        int index = 0;
        Integer lastRelevantIndex = null;
        List<Integer> irrelevantIndexes = new ArrayList<>();
        int indexShift = 0;
        while (index < nodes.size()) {
            ASTNode node = nodes.get(index);
            if (isNodeRelevantForGrammar(node)) {
                indexShift = 0;
                while (!irrelevantIndexes.isEmpty()) {
                    int irrelevantIndex = irrelevantIndexes.removeFirst();
                    ASTNode irrelevantNode = nodes.remove(irrelevantIndex + indexShift);
                    index--;
                    indexShift--;
                    node.prepend(irrelevantNode);
                }
                lastRelevantIndex = index;
            } else {
                irrelevantIndexes.add(index);
            }
            index++;
        }

        if (lastRelevantIndex != null && !irrelevantIndexes.isEmpty()) {
            ASTNode node = nodes.get(lastRelevantIndex);
            indexShift = 0;
            while (!irrelevantIndexes.isEmpty()) {
                int irrelevantIndex = irrelevantIndexes.removeFirst();
                ASTNode irrelevantNode = nodes.remove(irrelevantIndex + indexShift);
                indexShift--;
                node.append(irrelevantNode);
            }
        }

        return nodes;
    }

    public List<Token> lex(String code, @Nullable List<Token> previousTokens) {
        String hash = new String(md5.digest(code.getBytes(StandardCharsets.UTF_8)));
        if (!lexCache.containsKey(hash)) {
            List<Token> tokens = new ArrayList<>();

            AtomicInteger row = new AtomicInteger(1);
            AtomicInteger col = new AtomicInteger(1);
            AtomicInteger offset = new AtomicInteger(0);

            code = code.replaceAll("\r\n", "\n");
            code = code.replaceAll("\r", "\n");

            AtomicReference<String> codeRef = new AtomicReference<>(code);

            List<TokenMatcher> matchers = tokenMatchers();

            while (!code.isEmpty()) {
                int beforeLength = code.length();
                for (TokenMatcher matcher : matchers) {
                    if (codeRef.get().length() <= 0) {
                        break;
                    }

                    int lengthBefore = codeRef.get().length();
                    TokenDef tokenDef = matcher.lexNext(codeRef);

                    if (tokenDef != null) {
                        tokens.add(tokenDef.toToken(this, row.get(), col.get(), offset.get()));
                    }

                    String processedCode = codeRef.get().substring(0, lengthBefore - codeRef.get().length());

                    updateRowColOffsetForProcessed(offset, row, col, processedCode);
                }
                if (beforeLength == codeRef.get().length()) {
                    String invalidChar = codeRef.get().substring(0,1);
                    tokens.add(new Token(
                            this,
                            "T_INVALID",
                            invalidChar,
                            row.get(),
                            col.get(),
                            offset.get()
                    ));
                    updateRowColOffsetForProcessed(offset, row, col, invalidChar);
                    codeRef.set(codeRef.get().substring(1));
                }
            }
            lexCache.put(hash, tokens);
        }
        return lexCache.get(hash);
    }

    private void updateRowColOffsetForProcessed(
            AtomicInteger offset,
            AtomicInteger row,
            AtomicInteger col,
            String processedCode
    ) {
        int processedLength = processedCode.length();
        offset.set(offset.get() + processedLength);
        row.set(row.get() + StringUtils.countMatches(processedCode, "\n"));
        if (processedCode.contains("\n")) {
            col.set(col.get() + processedLength - processedCode.lastIndexOf("\n"));
        } else {
            col.set(col.get() + processedLength);
        }
    }

    private Map<String, List<NodePattern>> grammarMap() {
        if (grammarMap == null) {
            grammarMap = new HashMap<>();
            List<NodePattern> patterns = grammar();
            for (NodePattern pattern : patterns) {
                for (String key : pattern.consumedNodeKeys()) {
                    grammarMap.computeIfAbsent(key, k -> new ArrayList<>()).add(pattern);
                }
            }
        }
        return grammarMap;
    }
}
