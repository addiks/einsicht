package de.addiks.einsicht.abstract_syntax_tree;

import de.addiks.einsicht.languages.Language;
import org.jspecify.annotations.Nullable;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CodeBlock extends ASTNode {
    private final Map<ASTNode, Integer> childToIndex = new HashMap<>();

    public CodeBlock(
            Language language,
            int row,
            int col,
            int offset,
            @Nullable ASTNode parent
    ) {
        super(language, "", row, col, offset, "block", parent, List.of());
    }

    public void addStatement(ASTNode statement) {
        childToIndex.put(statement, children.size());
        children.add(statement);
        statement.setParent(this);
        code += statement.reconstructCode();
    }
}
