package de.addiks.einsicht.languages.abstract_syntax_tree;

import java.nio.file.Path;
import java.util.List;

public class ASTRoot extends ASTBranch {
    private final Path filepath;

    public ASTRoot(
            List<ASTNode> children,
            Path filepath
    ) {
        super(children, "root", null);
        this.filepath = filepath;
    }
}
