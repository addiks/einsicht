package de.addiks.einsicht.abstract_syntax_tree.selectors;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;

import java.util.List;

public class Conjunction implements ASTSelector {
    private final List<ASTSelector> parts;
    private final boolean isOr;
    public Conjunction(List<ASTSelector> parts, boolean isOr) {
        this.parts = parts;
        this.isOr = isOr;
    }

    public static Conjunction and(List<ASTSelector> parts) {
        return new Conjunction(parts, false);
    }
    public static Conjunction and(ASTSelector left, ASTSelector right) {
        return new Conjunction(List.of(left, right), false);
    }
    public static Conjunction or(List<ASTSelector> parts) {
        return new Conjunction(parts, true);
    }
    public static Conjunction or(ASTSelector left, ASTSelector right) {
        return new Conjunction(List.of(left, right), true);
    }

    @Override
    public boolean matches(ASTNode node) {
        for (ASTSelector selector : parts) {
            if (isOr == selector.matches(node)) {
                return isOr;
            }
        }
        return !isOr;
    }
}
