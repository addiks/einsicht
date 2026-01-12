package de.addiks.einsicht.view.widgets;

import de.addiks.einsicht.Hub;
import de.addiks.einsicht.filehandling.FileByLineNumberIndex;
import de.addiks.einsicht.filehandling.PartitionedFile;
import de.addiks.einsicht.filehandling.RowColumn;
import javafx.event.Event;
import javafx.event.EventType;
import javafx.geometry.Orientation;
import javafx.scene.control.ScrollBar;
import javafx.scene.input.KeyEvent;
import javafx.scene.layout.HBox;

import java.io.IOException;

public class EditorWindow extends HBox {
    private final Hub hub;
    private final PartitionedFile file;
    private final RowsWidget rows;
    private final ScrollBar scrollBar;

    public EditorWindow(Hub hub, PartitionedFile file) throws IOException {
        this(hub, file, new RowColumn(1,1));
    }

    public EditorWindow(Hub hub, PartitionedFile file, RowColumn position) throws IOException {
        super();

        this.hub = hub;

        FileByLineNumberIndex lineIndex = hub.get(FileByLineNumberIndex.class);

        rows = new RowsWidget(file, lineIndex, position);
        rows.prefWidthProperty().bind(this.widthProperty().subtract(16));
        rows.prefHeightProperty().bind(this.heightProperty());
        getChildren().add(rows);

        scrollBar = new ScrollBar();
        scrollBar.orientationProperty().set(Orientation.VERTICAL);
        scrollBar.setMinWidth(16);
        scrollBar.setMinHeight(100);
        getChildren().add(scrollBar);

        this.file = file;
    }


    public void processEvent(Event event) {
        if (event instanceof KeyEvent keyEvent && event.getEventType().getName().equals("KEY_PRESSED")) {
            rows.cursors().forEach(c -> c.onKeyPressed(keyEvent));
        }
    }
}
