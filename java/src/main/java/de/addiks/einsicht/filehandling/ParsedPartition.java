package de.addiks.einsicht.filehandling;

import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.filehandling.codings.MappedString;
import org.eclipse.jdt.annotation.NonNullByDefault;

import java.io.IOException;

@NonNullByDefault
public class ParsedPartition implements PartitionedFile.Partition {
    private ASTRoot syntaxTree;
    private final PartitionParser parser;
    public ParsedPartition(ASTRoot syntaxTree, PartitionParser parser) {
        this.syntaxTree = syntaxTree;
        this.parser = parser;
    }

    @Override
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

    @Override
    public PartitionedFile.Partition appendBy(PartitionedFile.Partition other) {
        if (other instanceof ParsedPartition parsedPartition) {
            return appendBy(parsedPartition);
        } else {
            throw new IllegalArgumentException("Can only merge parsed-partition with another parsed-partition!");
        }
    }

    public ParsedPartition appendBy(ParsedPartition other) {
        return parser.combine(this, other);
    }
}
