package de.addiks.einsicht.filehandling;

import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.filehandling.codings.BinaryString;
import de.addiks.einsicht.filehandling.codings.DecodedCharacter;
import de.addiks.einsicht.filehandling.codings.MappedString;

import java.io.IOException;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;

public class ParsedPartition implements FileTransaction.Partition {
    private ASTRoot syntaxTree;
    private final PartitionParser parser;
    public ParsedPartition(ASTRoot syntaxTree, PartitionParser parser) {
        this.syntaxTree = syntaxTree;
        this.parser = parser;
    }

    public ASTRoot syntaxTree() {
        return syntaxTree;
    }

    @Override
    public boolean modified() {
        return syntaxTree.isDirty();
    }

    @Override
    public MappedString currentContent() {
        return syntaxTree.reconstructCode();
    }

    @Override
    public void resetTo(
            MappedString content
    ) throws IOException {
        syntaxTree = parser.parse(content, 0);
    }
}
