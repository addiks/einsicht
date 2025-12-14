package de.addiks.einsicht.languages;

import de.addiks.einsicht.Hub;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.patterns.NodePattern;
import de.addiks.einsicht.semantics.Semantic;
import de.addiks.einsicht.tokens.Token;
import de.addiks.einsicht.tokens.TokenMatcher;
import de.addiks.einsicht.tokens.matchers.DirectTokenMatcher;
import de.addiks.einsicht.tokens.matchers.KeywordsTokenMatcher;
import de.addiks.einsicht.tokens.matchers.LiteralTokenMatcher;
import de.addiks.einsicht.tokens.matchers.RegexMatcher;

import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class JavaLanguage extends Language {
    public JavaLanguage(Hub hub) {
        super(hub);
    }

    @Override
    public String name() {
        return "Java";
    }

    @Override
    public List<TokenMatcher> tokenMatchers() {
        return List.of(
                new KeywordsTokenMatcher(List.of(
                        "package", "import",
                        "public", "protected", "private",
                        "static", "abstract", "final",
                        "new", "class", "interface", "enum", "record",
                        "return", "break", "continue", "throw",
                        "void", "null", "boolean", "int", "long", "double",
                        "if", "else", "while", "for",
                        "try", "catch", "finally",
                        "assert",
                        "switch", "case"
                )),
                new RegexMatcher(Pattern.compile("\\n( +)?"), "T_INDENTATION"),
                new RegexMatcher(Pattern.compile("\\s+"), "T_WHITESPACE"),
                new RegexMatcher(Pattern.compile("[a-zA-Z_][a-zA-Z0-9_]+"), "T_SYMBOL"),
                new RegexMatcher(Pattern.compile("[0-9_]+(\\.[0-9]*)?"), "T_NUMBER"),
                new RegexMatcher(Pattern.compile("//([^\\n]*)"), "T_COMMENT"),
                new RegexMatcher(Pattern.compile("/\\*.*\\*/"), "T_COMMENT"),
                new DirectTokenMatcher(List.of(
                        ".", ",", "(", ")", "[", "]", "{", "}", ":", "="
                ), "T_SPECIAL_CHAR"),
                new DirectTokenMatcher(List.of("=", "+=", "-=", "*=", "/="), "T_ASSIGN"),
                new DirectTokenMatcher(List.of("+", "-", "*", "/"), "T_OPERATOR"),
                new LiteralTokenMatcher('\'', "T_LITERAL"),
                new LiteralTokenMatcher('"', "T_LITERAL")
        );
    }

    @Override
    public boolean isNodeRelevantForGrammar(ASTNode node) {
        if (node instanceof Token token) {
            return !List.of("T_WHITESPACE", "T_COMMENT", "T_INDENTATION").contains(token.tokenName());
        }
        return true;
    }

    @Override
    public List<NodePattern> grammar() {
        return List.of();
    }

    @Override
    public Map<String, Semantic.Factory> semantics() {
        return Map.of();
    }

    @Override
    public Object stylesheet() {
        return null;
    }

}
