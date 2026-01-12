package de.addiks.einsicht.languages;

import de.addiks.einsicht.Hub;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.patterns.NodeBranch;
import de.addiks.einsicht.abstract_syntax_tree.patterns.NodePattern;
import de.addiks.einsicht.abstract_syntax_tree.patterns.TokenNodePattern;
import de.addiks.einsicht.semantics.Semantic;
import de.addiks.einsicht.abstract_syntax_tree.tokens.TokenMatcher;
import de.addiks.einsicht.abstract_syntax_tree.tokens.matchers.RegexMatcher;
import org.eclipse.jdt.annotation.NonNullByDefault;

import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

@NonNullByDefault
public class UnknownLanguage extends Language {
    public UnknownLanguage(Hub hub) {
        super(hub);
    }

    @Override
    public String name() {
        return "Unknown";
    }

    @Override
    public List<TokenMatcher> tokenMatchers() {
        return List.of(
                new RegexMatcher(Pattern.compile("\\s+"), "T_SPACE"),
                new RegexMatcher(Pattern.compile("\\S+"), "T_CONTEXT")
        );
    }

    @Override
    public List<NodePattern> grammar() {
        return List.of(
                new NodeBranch("unknown", List.of(
                        new TokenNodePattern("T_UNKNOWN")
                ))
        );
    }

    public Map<String, Semantic.Factory> semantics() {
        return Map.of();
    }

    @Override
    public Object stylesheet() {
        return null;
    }

    @Override
    public boolean isNodeRelevantForGrammar(ASTNode node) {
        return true;
    }
}
