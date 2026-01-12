package de.addiks.einsicht.view.widgets;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import de.addiks.einsicht.filehandling.RowColumn;
import de.addiks.einsicht.view.widgets.abstract_syntax_tree.ASTCharacterWidget;
import de.addiks.einsicht.view.widgets.abstract_syntax_tree.ASTRowWidget;
import de.addiks.einsicht.view.widgets.abstract_syntax_tree.ASTWidget;
import javafx.event.Event;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.Region;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import org.eclipse.jdt.annotation.NonNullByDefault;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

@NonNullByDefault
public class TextCursor extends Region {
    private static final ScheduledExecutorService blinkExecutor = Executors.newSingleThreadScheduledExecutor();
    private static final ScheduledFuture<?> blinkFuture = blinkExecutor.scheduleAtFixedRate(TextCursor::toggleAllCursorsBlinkStatus, 1, 1, TimeUnit.SECONDS);
    private static final List<TextCursor> instances = new ArrayList<>();
    private static final Image glyph = new Image(TextCursor.class.getResource("/cursor.svg").toExternalForm());
    private static final Logger log = LoggerFactory.getLogger(TextCursor.class);

    private static boolean blinkStatus = false;

    private final RowsWidget rowsWidget;
    private final Rectangle shape;

    private ASTRowWidget rowWidget;
    private ASTNode node;
    private long offsetInNode;

    public TextCursor(RowsWidget rowsWidget, RowColumn position) {
        super();
        this.rowsWidget = rowsWidget;
        rowWidget = rowsWidget.row(position.row());
        var nodeOffset = rowColumnToNodeOffset(position);
        node = nodeOffset.node;
        offsetInNode = nodeOffset.offsetInNode;

        prefHeightProperty().bind(rowWidget.heightProperty());
        setWidth(2.0);

        double layoutX = 0.0;
        ASTCharacterWidget characterWidget = rowWidget.firstCharacter();
        for (int column = 1; column < position.column() && characterWidget != null; column++) {
            characterWidget = characterWidget.next();
        }
        if (characterWidget != null) {
            layoutX = characterWidget.getLayoutX();
        }

        setLayoutX(layoutX);
        layoutYProperty().bind(rowWidget.layoutYProperty());

        shape = new Rectangle(getWidth(), 24, Color.BLACK);
        shape.heightProperty().bind(rowWidget.heightProperty());
        getChildren().add(shape);

        instances.add(this);
        showCursorGlyph();
    }

    public void move(RowColumn position) {
        if (position.row() != rowWidget.lineNumber()) {
            rowWidget = rowsWidget.row(position.row());
            // TODO: remove from old, add to new
        }
        var nodeOffset = rowColumnToNodeOffset(position);
        this.node = nodeOffset.node;
        this.offsetInNode = Math.min(nodeOffset.offsetInNode, node.end().offset() - node.offset());
    }

    public RowColumn position() {
        return nodeOffsetToRowColumn(new PositionInAST(node, offsetInNode));
    }

    public static void shutdownAllCursors() {
        blinkFuture.cancel(true);
    }

    private PositionInAST rowColumnToNodeOffset(RowColumn position) {
        ASTRowWidget row = rowsWidget.row(position.row());

        Token token = row.tokenAtColumn(position.column());

        int offsetInNode = 0;
        if (token != null) {
            if (token.row() == position.row()) {
                offsetInNode = position.column() - token.column();
            } else {
                int tokenRow = token.row();
                for(String line : token.code().asString().split("\n")) {
                    if (tokenRow == position.row()) {
                        offsetInNode += position.column();
                    } else {
                        offsetInNode += line.length();
                    }
                    tokenRow++;
                }
            }
            return new PositionInAST(token, offsetInNode);
        } else {
            return new PositionInAST(row.content().getFirst().node().root(), offsetInNode);
        }
    }

    private RowColumn nodeOffsetToRowColumn(PositionInAST position) {
        var rowColPos = position.node.position();

        // TODO: This can prabably be done more efficiently.
        return rowColPos.advance(position.node.reconstructCode().substring(0, (int) position.offsetInNode));
    }

    private record PositionInAST(ASTNode node, long offsetInNode) {}

    public void onKeyPressed(KeyEvent event) {
        System.out.println(event);
    }

    private void updateBlinkStatus() {
        if (blinkStatus) {
            showCursorGlyph();
        } else {
            hideCursorGlyph();
        }
    }

    private void showCursorGlyph() {
        shape.setVisible(true);
    }

    private void hideCursorGlyph() {
        shape.setVisible(false);
    }

    private static void toggleAllCursorsBlinkStatus() {
        blinkStatus = !blinkStatus;
        instances.forEach(TextCursor::updateBlinkStatus);
    }

}
