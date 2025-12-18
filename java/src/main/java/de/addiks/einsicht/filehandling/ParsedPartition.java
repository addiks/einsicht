package de.addiks.einsicht.filehandling;

import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;

public class ParsedPartition implements FileTransaction.Partition {
    private final ASTRoot syntaxTree;
    public ParsedPartition(ASTRoot syntaxTree) {
        this.syntaxTree = syntaxTree;
    }

    public ASTRoot syntaxTree() {
        return syntaxTree;
    }

    @Override
    public boolean modified() {
        return false;
    }

    @Override
    public byte[] currentContent() {
        return new byte[0];
    }

    @Override
    public void resetTo(byte[] content) {

    }
}
