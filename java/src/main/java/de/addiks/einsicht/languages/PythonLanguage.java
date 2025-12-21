package de.addiks.einsicht.languages;

import de.addiks.einsicht.Hub;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.patterns.*;
import de.addiks.einsicht.abstract_syntax_tree.selectors.ASTSelector;
import de.addiks.einsicht.semantics.ClassHead;
import de.addiks.einsicht.semantics.FunctionHead;
import de.addiks.einsicht.semantics.Semantic;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import de.addiks.einsicht.abstract_syntax_tree.tokens.TokenMatcher;
import de.addiks.einsicht.abstract_syntax_tree.tokens.matchers.DirectTokenMatcher;
import de.addiks.einsicht.abstract_syntax_tree.tokens.matchers.KeywordsTokenMatcher;
import de.addiks.einsicht.abstract_syntax_tree.tokens.matchers.LiteralTokenMatcher;
import de.addiks.einsicht.abstract_syntax_tree.tokens.matchers.RegexMatcher;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class PythonLanguage extends Language {
    public PythonLanguage(Hub hub) {
        super(hub);
    }

    @Override
    public String name() {
        return "Python";
    }

    @Override
    public List<TokenMatcher> tokenMatchers() {
        return List.of(
                new KeywordsTokenMatcher(List.of(
                        "from", "import", "assert",
                        "def", "pass", "class", "lambda",
                        "if", "elif", "else", "not",
                        "return", "break", "continue",
                        "raise", "except", "try", "finally",
                        "while", "for", "match", "case",
                        "True", "False", "None",
                        "and", "or", "xor", "not",
                        "del", "as", "in", "breakpoint"
                )),
                new RegexMatcher(Pattern.compile("\\n( +)?(?=\\n)"), "T_INDENTATION_SUPERFLOUS"),
                new RegexMatcher(Pattern.compile("\\n( +)?"), "T_INDENTATION"),
                new RegexMatcher(Pattern.compile("\\s+"), "T_WHITESPACE"),
                new DirectTokenMatcher("@", "T_DECORATOR"),
                new RegexMatcher(Pattern.compile("[a-zA-Z_][a-zA-Z0-9_]+"), "T_SYMBOL"),
                new RegexMatcher(Pattern.compile("[0-9_]+(\\.[0-9]*)?"), "T_NUMBER"),
                new RegexMatcher(Pattern.compile("#([^\\n]*)"), "T_COMMENT"),
                new DirectTokenMatcher(List.of(".", ",", "(", ")", "[", "]", "{", "}", ":", "="), "T_SPECIAL_CHAR"),
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
        LateDefinedASTPattern expression = new LateDefinedASTPattern("expression");

        NodeSequence identifier = new NodeSequence("identifier", List.of(
                new TokenNodePattern("T_SYMBOL"),
                new RepeatingNode("identifier-path", new NodeSequence("identifier-element", List.of(
                        new TokenNodePattern("."),
                        new TokenNodePattern("T_SYMBOL")
                )), true)
        ));

        NodeSequence importFrom = new NodeSequence("import-from", List.of(
                new TokenNodePattern("T_FROM"),
                new RepeatingNode("import-from-parent", new TokenNodePattern("."), true),
                identifier
        ));

        NodeSequence importStatement = new NodeSequence("import", List.of(
                new OptionalNode(importFrom),
                new TokenNodePattern("T_IMPORT"),
                identifier
        ));

        NodeSequence tuple = new NodeSequence("tuple", List.of(
                new TokenNodePattern("("),
                new RepeatingNode("tuple-content", new NodeSequence("tuple-element", List.of(
                        expression,
                        new OptionalNode(new TokenNodePattern(","))
                )), true),
                new TokenNodePattern(")")
        ));

        NodeSequence list = new NodeSequence("list", List.of(
                new TokenNodePattern("["),
                new RepeatingNode("list-content", new NodeSequence("list-element", List.of(
                        expression,
                        new OptionalNode(new TokenNodePattern(","))
                )), true)
        ));

        NodeSequence call = new NodeSequence("call", List.of(
                identifier,
                tuple
        ));

        NodeSequence raiseDef = new NodeSequence("raise", List.of(
                new TokenNodePattern("T_RAISE"),
                identifier,
                tuple
        ));

        NodeSequence decorator = new NodeSequence("decorator", List.of(
                new TokenNodePattern("@"),
                identifier,
                new OptionalNode(tuple)
        ));

        NodeSequence operation = new NodeSequence("operation", List.of(
                expression,
                new TokenNodePattern("T_OPERATOR"),
                expression
        ));

        NodeSequence assignment = new NodeSequence("assignment", List.of(
                expression,
                new TokenNodePattern("="),
                expression
        ));

        NodeSequence classDefinition = new NodeSequence("class", List.of(
                new TokenNodePattern("T_CLASS"),
                identifier,
                tuple,
                new TokenNodePattern(":")
        ));

        NodeSequence functionDefinition = new NodeSequence("function", List.of(
                new TokenNodePattern("T_DEF"),
                identifier,
                tuple,
                new TokenNodePattern(":")
        ));

        NodeBranch bool = new NodeBranch("boolean", List.of(
                new TokenNodePattern("T_TRUE"),
                new TokenNodePattern("T_FALSE")
        ));

        NodeBranch expressionElement = new NodeBranch("expression-element", List.of(
                identifier,
                call,
                bool,
                list,
                tuple,
                new TokenNodePattern("T_LITERAL"),
                new TokenNodePattern("T_NUMBER")
                // operation # TODO: Infinite loop? expr => operation => expression => ... HOW?!
        ));

        NodeBranch expressionSuffix = new NodeBranch("expression-suffix", List.of(list));

        expression.definePattern(new NodeSequence("expression", List.of(
                expressionElement,
                new RepeatingNode("expression-suffixes", expressionSuffix, true)
        )));

        return List.of(
                importStatement,
                importFrom,
                identifier,
                tuple,
                list,
                bool,
                classDefinition,
                functionDefinition,
                raiseDef,
                call,
                decorator,
                operation,
                assignment,
                expression,
                expressionElement
        );
    }

    @Override
    public Map<String, Semantic.Factory> semantics() {
        Map<String, Semantic.Factory> semantics = new HashMap<>();

        semantics.put("class", new ClassHead.Factory(
                ASTSelector.of("class/identifier")
        ));

        semantics.put("function", new FunctionHead.Factory(
                ASTSelector.of("function/identifier")
        ));

        return semantics;
    }

    @Override
    public Object stylesheet() {
        return null;
    }
}
