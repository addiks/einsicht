package de.addiks.einsicht.view.widgets;

import de.addiks.einsicht.filehandling.PartitionedFile;
import javafx.beans.binding.Bindings;
import javafx.geometry.Orientation;
import javafx.scene.control.ScrollBar;
import javafx.scene.layout.AnchorPane;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Pane;

import java.awt.*;

public class EditorCanvas extends HBox {
    private final PartitionedFile file;
    private final Pane context;
    private final ScrollBar scrollBar;

    public EditorCanvas(PartitionedFile file) {
        super();

        context = new Pane();
        context.prefWidthProperty().bind(this.widthProperty().subtract(16));
        context.prefHeightProperty().bind(this.heightProperty());

        scrollBar = new ScrollBar();
        scrollBar.orientationProperty().set(Orientation.VERTICAL);
        scrollBar.setMinWidth(16);
        scrollBar.setMinHeight(100);

        getChildren().add(context);
        getChildren().add(scrollBar);

        this.file = file;
    }


}
