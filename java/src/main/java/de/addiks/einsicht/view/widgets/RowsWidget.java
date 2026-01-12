package de.addiks.einsicht.view.widgets;

import de.addiks.einsicht.abstract_syntax_tree.ASTIterator;
import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.filehandling.FileByLineNumberIndex;
import de.addiks.einsicht.filehandling.PartitionedFile;
import de.addiks.einsicht.filehandling.RowColumn;
import de.addiks.einsicht.view.widgets.abstract_syntax_tree.*;
import javafx.scene.layout.Pane;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import org.eclipse.jdt.annotation.NonNullByDefault;
import org.jspecify.annotations.NonNull;
import org.jspecify.annotations.Nullable;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@NonNullByDefault
public class RowsWidget extends StackPane implements ASTRowWidgetContainer {
    private static final int PARTITION_READ_SIZE = 16 * 1024;
    private final Map<Integer, ASTRowWidget> rows = new HashMap<>();
    private final VBox rowVBox = new VBox();
    private final List<TextCursor> cursors = new ArrayList<>();
    private final Pane cursorPane = new Pane();

    public RowsWidget(
            PartitionedFile file,
            FileByLineNumberIndex lineIndex,
            RowColumn position
    ) throws IOException {

        getChildren().add(rowVBox);

     //   cursorPane.setPickOnBounds(false); // cursorPane should not accept clicks (yet?)
        getChildren().add(cursorPane);

        PartitionedFile.PartitionAtArea partitionAtArea = file.partitionFor(
                lineIndex.offsetAtLine(position.row()),
                PARTITION_READ_SIZE
        );

        ASTRoot root = partitionAtArea.partition().syntaxTree();

        for (ASTRowWidget row : readASTIntoRows(root)) {
            int lineNumber = row.lineNumber();
            if (rows.containsKey(lineNumber)) {
                row = row.merge(rows.get(lineNumber));
            }
            rows.put(row.lineNumber(), row);
        }

        for (ASTRowWidget rowWidget : rows.values()) {
            add(rowWidget);
        }

        TextCursor cursor = new TextCursor(this, position);
        cursors.add(cursor);
        cursorPane.getChildren().add(cursor);
    }

    public List<TextCursor> cursors() {
        return cursors;
    }

    public void add(ASTRowWidget rowWidget) {
        rows.put(rowWidget.lineNumber(), rowWidget);
        rowVBox.getChildren().add(rowWidget);
    }

    public int size() {
        return rows.size();
    }

    public ASTRowWidget row(int line) {
        if (line > rows.size()) {
            throw new IllegalArgumentException("Cannot get row widget for line %d when only %d lines are present!".formatted(
                    line,
                    rows.size()
            ));
        }
        return rows.get(line);
    }

    private List<ASTRowWidget> readASTIntoRows(ASTRoot root) {

        Map<Integer, List<ASTWidget<?>>> widgetsPerRow = new HashMap<>();
        Map<Integer, List<ASTCharacterWidget>> charactersPerRow = new HashMap<>();

        // Converts the ASTNode-tree into an ASTWidget-tree while storing resulting ASTWidget's per row
        ASTWidget<?> rootWidget = ASTIterator.deepMap(
                root,
                node -> {
                    ASTWidget<?> widget = ASTWidget.of(node);
                    int lastRow = node.lastRow();
                    for (int row = node.row(); row <= lastRow; row++) {
                        widgetsPerRow.computeIfAbsent(row, l -> new ArrayList<>()).add(widget);
                        if (widget instanceof ASTTokenWidget tokenWidget) {
                            for (ASTCharacterWidget character : tokenWidget.characters()) {
                                charactersPerRow.computeIfAbsent(row, l -> new ArrayList<>()).add(character);
                            }
                        }
                    }
                    return widget;
                },
                (ASTWidget<?> parent, List<ASTWidget<?>> children) -> {
                    if (parent instanceof ASTBranchWidget branchWidget) {
                        ASTBranchWidget newParent = new ASTBranchWidget(
                                branchWidget.node(),
                                children
                        );
                        int lastRow = parent.to().row();
                        for (int row = parent.from().row(); row <= lastRow; row++) {
                            if (widgetsPerRow.containsKey(row)) {
                                List<ASTWidget<?>> widgetsInRow = widgetsPerRow.get(row);
                                if (widgetsInRow.contains(parent)) {
                                    widgetsInRow.remove(parent);
                                    widgetsInRow.add(newParent);
                                }
                                for (ASTWidget<?> child : children) {
                                    widgetsInRow.remove(child);
                                }
                            }
                        }
                        parent = newParent;
                    }
                    return parent;
                }
        );

        List<ASTRowWidget> rows = new ArrayList<>();
        for (int row : widgetsPerRow.keySet()) {
            var rowWidget = new ASTRowWidget(this, row, widgetsPerRow.get(row), charactersPerRow.get(row));
            rows.add(rowWidget);
        }
        return rows;
    }

}
