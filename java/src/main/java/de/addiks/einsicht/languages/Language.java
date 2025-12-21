package de.addiks.einsicht.languages;

import de.addiks.einsicht.Hub;
import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.abstract_syntax_tree.patterns.NodePattern;
import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.semantics.Semantic;
import de.addiks.einsicht.abstract_syntax_tree.tokens.ConsumableString;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import de.addiks.einsicht.abstract_syntax_tree.tokens.TokenDef;
import de.addiks.einsicht.abstract_syntax_tree.tokens.TokenMatcher;
import org.jspecify.annotations.Nullable;

import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

public abstract class Language {
    private static final MessageDigest md5;
    static {
        try {
            md5 = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }

    private final Map<String, List<ASTNode>> lexCache = new HashMap<>();
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

    public abstract boolean isNodeRelevantForGrammar(ASTNode node);

    public abstract List<NodePattern> grammar();

    public abstract Map<String, Semantic.Factory> semantics();

    public List<ASTNode> groupStatementsIntoBlocks(List<ASTNode> nodes) {
        return nodes;
    }

    public abstract Object stylesheet();

    public ParseResult parse(
            MappedString code,
            Path filepath,
            int startingRow,
            int startingColumn,
            long startingOffset
    ) {
        String hash = new String(md5.digest(code.toByteArray()));
        if (!parseCache.containsKey(hash)) {
            List<ASTNode> tokens = lex(code, startingRow, startingColumn, startingOffset);
            if (!tokens.isEmpty()) {
                Map<String, List<NodePattern>> grammar = grammarMap();

                normalize(tokens);

                List<ASTNode> nodes = applyGrammar(tokens, grammar);
                nodes = groupStatementsIntoBlocks(nodes);

                if (debugEnabled()) {
                    dumpAST(nodes);
                }

                ASTRoot ast = new ASTRoot(nodes, filepath);
                addSemanticsTo(ast);

                hub.register(ast);

                parseCache.put(hash, new ParseResult(ast, tokens));
            }
        }
        return parseCache.getOrDefault(hash, new ParseResult(null, List.of()));
    }

    public record ParseResult(
            @Nullable ASTRoot previousAST,
            List<ASTNode> previousTokens
    ) {}

    private void addSemanticsTo(ASTRoot ast) {

        // Preparations
        Map<String, Semantic.Factory> semanticFactories = semantics();
        Map<Class<? extends Semantic>, List<Semantic>> semantics = new HashMap<>();
        Map<Class<? extends Semantic>, Semantic.Factory.Contextual> contextualFactories = new HashMap<>();
        for (Semantic.Factory factory : semanticFactories.values()) {
            if (factory instanceof Semantic.Factory.Contextual contextualFactory) {
                contextualFactories.put(contextualFactory.root(), contextualFactory);
            }
        }

        // Determine local (per-node) semantics
        ast.iterate(node -> {
            String key = node.grammarKey();
            if (semanticFactories.containsKey(key)
                    && node instanceof ASTBranch branch
                    && semanticFactories.get(key) instanceof Semantic.Factory.Local localFactory) {
                Semantic.Local semantic = localFactory.forBranch(branch);
                branch.assignSemantic(semantic);
                semantics.computeIfAbsent(semantic.getClass(), c -> new ArrayList<>()).add(semantic);
            }
        });

        // Combine local semantics into contextual semantics
        for (List<Semantic> semanticsForClass : semantics.values()) {
            for (Semantic semantic : semanticsForClass) {

                if (contextualFactories.containsKey(semantic.getClass())) {
                    Semantic.Factory.Contextual contextualFactory = contextualFactories.get(semantic.getClass());

                    List<Semantic> related = new ArrayList<>();
                    for (Class<? extends Semantic> relatedClass : contextualFactory.related()) {
                        for (Semantic possiblyRelated : semantics.get(relatedClass)) {
                            if (contextualFactory.isRelatedTo(semantic, possiblyRelated)) {
                                related.add(possiblyRelated);
                            }
                        }
                    }

                    Semantic.Contextual contextual = contextualFactory.combine(semantic, related);


                }
            }
        }

    }

    private List<ASTNode> applyGrammar(List<ASTNode> nodes, Map<String, List<NodePattern>> grammar) {
        Map<String, List<ASTNode>> nodeMap = mapNodes(nodes);
        while (!nodeMap.isEmpty()) {
            boolean hasMutated = false;
            for (String grammarKey : nodeMap.keySet()) {
                if (!grammar.containsKey(grammarKey)) {
                    continue;
                }
                for (ASTNode node : new ArrayList<>(nodeMap.get(grammarKey))) {
                    for (NodePattern pattern : grammar.get(grammarKey)) {

                        Integer nodeIndex = node.offsetIn(nodes);
                        if (nodeIndex == null) {
                            break;
                        }

                        if (pattern.matches(nodes, nodeIndex)) {
                            NodePattern.MutationResult result = pattern.mutate(nodes, nodeIndex);

                            for (ASTNode replacedNode : result.addedNodes()) {
                                hasMutated = true;

                                String replacedNodeKey = replacedNode.grammarKey();
                                nodeMap.get(replacedNodeKey).remove(replacedNode);
                                if (nodeMap.get(replacedNodeKey).isEmpty()) {
                                    nodeMap.remove(replacedNodeKey);
                                }

                                String code = replacedNode.getCode().asString();
                                if (nodeMap.containsKey(code) && nodeMap.get(code).contains(replacedNode)) {
                                    nodeMap.get(code).remove(replacedNode);
                                    if (nodeMap.get(code).isEmpty()) {
                                        nodeMap.remove(code);
                                    }
                                }
                            }

                            if (result.newIndex() != null) {
                                hasMutated = true;
                                ASTNode newNode = nodes.get(result.newIndex());
                                nodeMap.computeIfAbsent(newNode.grammarKey(), k -> new ArrayList<>()).add(newNode);
                            }
                        }
                    }
                }
                if (nodeMap.containsKey(grammarKey) && nodeMap.get(grammarKey).isEmpty()) {
                    nodeMap.remove(grammarKey);
                }
            }
            if (!hasMutated) {
                break;
            }
        }
        return nodes;
    }

    private Map<String, List<ASTNode>> mapNodes(List<ASTNode> nodes) {
        Map<String, List<ASTNode>> nodeMap = new HashMap<>();
        for (ASTNode node : nodes) {
            if (node instanceof Token token) {
                nodeMap.computeIfAbsent(token.tokenName(), t -> new ArrayList<>()).add(token);
                nodeMap.computeIfAbsent(token.getCode().asString(), t -> new ArrayList<>()).add(token);
            }
        }
        return nodeMap;
    }

    private void normalize(List<ASTNode> nodes) {
        int index = 0;
        Integer lastRelevantIndex = null;
        List<Integer> irrelevantIndexes = new ArrayList<>();
        int indexShift;
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
    }

    public List<ASTNode> lex(
            MappedString code,
            int startingRow,
            int startingColumn,
            long startingOffset
    ) {
        String hash = new String(md5.digest(code.toByteArray()));
        if (!lexCache.containsKey(hash)) {
            List<ASTNode> tokens = new ArrayList<>();

            AtomicInteger row = new AtomicInteger(startingRow);
            AtomicInteger col = new AtomicInteger(startingColumn);
            AtomicLong offset = new AtomicLong(startingOffset);

        //    code = code.replaceAll("\r\n", "\n");
        //    code = code.replaceAll("\r", "\n");

            ConsumableString consumableCode = new ConsumableString(code);
            List<TokenMatcher> matchers = tokenMatchers();

            while (!code.isEmpty()) {
                int beforeLength = code.length();
                for (TokenMatcher matcher : matchers) {
                    int lengthBefore = consumableCode.length();
                    if (lengthBefore <= 0) {
                        break;
                    }

                    TokenDef tokenDef = matcher.lexNext(consumableCode);
                    if (tokenDef != null) {
                        tokens.add(tokenDef.toToken(this, row.get(), col.get(), offset.get()));
                    }

                    MappedString processedCode = consumableCode.consumed(lengthBefore - consumableCode.length());
                    updateRowColOffsetForProcessed(offset, row, col, processedCode);
                }
                if (beforeLength == consumableCode.length()) {
                    MappedString invalidChar = consumableCode.substring(0,1);
                    tokens.add(new Token(
                            this,
                            "T_INVALID",
                            invalidChar,
                            row.get(),
                            col.get(),
                            offset.get()
                    ));
                    updateRowColOffsetForProcessed(offset, row, col, invalidChar);
                    consumableCode.consume(1);
                }
            }
            lexCache.put(hash, tokens);
        }
        return lexCache.get(hash);
    }

    private void updateRowColOffsetForProcessed(
            AtomicLong offset,
            AtomicInteger row,
            AtomicInteger col,
            MappedString processedCode
    ) {
        int processedLength = processedCode.length();
        offset.set(offset.get() + processedLength);
        row.set(row.get() + processedCode.substringCount("\n"));
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

    public static void dumpAST(List<ASTNode> nodes) {
        dumpAST(nodes, 0, null);
    }

    public static void dumpAST(List<ASTNode> nodes, int level, @Nullable Integer depth) {
        if (depth != null && level + 1 > depth) {
            return;
        }
        for (ASTNode node : nodes) {
            String nodeDescr = "node: " + node.getGrammarKey();
            if (node instanceof Token token) {
                nodeDescr = token.tokenName() + " - " + token.getCode().asString().trim();
            }
            System.out.println(
                    String.format("%1$3s", node.getRow()).replace(' ', '0') +
                    "-" +
                    String.format("%1$" + level + "s", "|") +
                    nodeDescr +
                    ">" +
                    node.getCode().asString().trim()
            );
        }
        if (level == 0) {
            System.out.println();
        }
    }
}
