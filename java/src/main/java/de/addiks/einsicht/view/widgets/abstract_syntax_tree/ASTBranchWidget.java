package de.addiks.einsicht.view.widgets.abstract_syntax_tree;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.filehandling.RowColumn;
import org.eclipse.jdt.annotation.NonNullByDefault;
import org.jspecify.annotations.NonNull;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@NonNullByDefault
public class ASTBranchWidget extends ASTWidget<ASTBranch> {
    private final List<? extends ASTWidget<?>> children;

    public ASTBranchWidget(ASTBranch node, List<? extends ASTWidget<?>> children) {
        super(node);
        this.children = children;
    }

    public ASTBranchWidget(
            ASTBranch node,
            List<ASTWidget<?>> children,
            RowColumn start,
            RowColumn end
    ) {
        super(node, start, end);
        this.children = children;
    }

    public static ASTBranchWidget of(@NonNull ASTBranch branch) {
        List<ASTWidget<?>> children = new ArrayList<>();
        for (ASTNode node : branch.allChildren()) {
            children.add(ASTWidget.of(node));
        }
        return new ASTBranchWidget(branch, children);
    }

    public List<? extends ASTWidget<?>> children() {
        return children;
    }

    @Override
    public Map<Integer, ASTWidget<ASTBranch>> separateByRows() {

        Map<Integer, ASTWidget<ASTBranch>> rows = new HashMap<>();
        Map<Integer, List<ASTNode>> childrenByRow = new HashMap<>();
        ASTBranch branch = node();

        for (ASTNode node : branch.allChildren()) {
            int lastRow = node.lastRow();
            for (int lineNumber = node.row(); lineNumber <= lastRow; lineNumber++) {
                childrenByRow.computeIfAbsent(lineNumber, l -> new ArrayList<>()).add(node);
            }
        }

        for (int lineNumber : childrenByRow.keySet()) {
            List<ASTWidget<?>> childWidgets = new ArrayList<>();
            for (ASTNode child : childrenByRow.get(lineNumber)) {
                childWidgets.add(ASTWidget.of(child));
            }

            rows.put(lineNumber, new ASTBranchWidget(
                    branch,
                    childWidgets,
                    new RowColumn(lineNumber, 0),
                    new RowColumn(lineNumber, 9999) // TODO
            ));
        }

        return rows;
    }

    @Override
    public ASTWidget<ASTBranch> merge(ASTWidget<ASTBranch> other) {
        return null;
    }
}
