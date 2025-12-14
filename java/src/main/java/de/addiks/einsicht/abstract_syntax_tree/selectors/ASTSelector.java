package de.addiks.einsicht.abstract_syntax_tree.selectors;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public interface ASTSelector {
    boolean matches(ASTNode node);

    default List<ASTNode> selectIn(ASTNode node) {
        List<ASTNode> nodes = new ArrayList<>();
        node.iterate(n -> {
            if (matches(n)) {
                nodes.add(n);
            }
        });
        return nodes;
    }

    static ASTSelector of(String query) {
        List<ASTSelector> orElements = new ArrayList<>();
        for (String part : query.split(",")) {
            List<String> elements = new ArrayList<>(Arrays.asList(part.split("/")));
            List<ASTSelector> andElements = new ArrayList<>();
            int depth = 0;
            while (!elements.isEmpty()) {
                String element = elements.removeLast();
                ASTSelector elementSelector;
                if (element.isBlank() && elements.isEmpty()) {
                    elementSelector = new IsRootSelector();
                } else {
                    elementSelector = new ByGrammarKey(element);
                }
                for (int i=0; i<depth; i++) {
                    elementSelector = new ParentSelector(elementSelector);
                }
                andElements.add(elementSelector);
                depth++;
            }
            orElements.add(Conjunction.and(andElements));
        }
        return Conjunction.or(orElements);
    }
}
