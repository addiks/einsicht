package de.addiks.einsicht.abstract_syntax_tree;

import de.addiks.einsicht.languages.Language;
import org.jspecify.annotations.Nullable;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CodeBlock extends ASTBranch {

    public CodeBlock(
            List<ASTNode> children
    ) {
        super(children, "block");
    }

}
