package de.addiks.einsicht.view.widgets.abstract_syntax_tree;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import de.addiks.einsicht.filehandling.RowColumn;
import javafx.scene.Node;
import javafx.scene.layout.Pane;
import javafx.scene.layout.Region;
import org.eclipse.jdt.annotation.NonNullByDefault;
import org.jspecify.annotations.Nullable;

import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;

@NonNullByDefault
public abstract class ASTWidget<N extends ASTNode> extends Pane {
    private final N node;
    private final RowColumn from;
    private final RowColumn to;

    public ASTWidget(N node) {
        this(node, node.position(), node.position());
    }

    public ASTWidget(N node, RowColumn from, RowColumn to) {
        super();
        this.node = node;
        this.from = from;
        this.to = to;
    }

    public N node() {
        return node;
    }

    public RowColumn from() {
        return from;
    }

    public RowColumn to() {
        return to;
    }

    public abstract Map<Integer, ASTWidget<N>> separateByRows();

    public abstract ASTWidget<N> merge(ASTWidget<N> other);

    public static <N2 extends ASTNode> ASTWidget<N2> of(N2 node) {
        if (node instanceof Token token) {
            return (ASTWidget<N2>) ASTTokenWidget.of(token);

        } else if (node instanceof ASTBranch branch) {
            return (ASTWidget<N2>) ASTBranchWidget.of(branch);
        }
        throw new IllegalArgumentException("Cannot convert AST node of %s into ASTWidget!".formatted(
                node.getClass().getName()
        ));
    }
}
