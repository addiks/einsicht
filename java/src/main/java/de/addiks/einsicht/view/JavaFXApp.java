package de.addiks.einsicht.view;

import de.addiks.einsicht.Hub;
import de.addiks.einsicht.filehandling.PartitionedFile;
import de.addiks.einsicht.view.widgets.EditorCanvas;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.ScrollPane;
import javafx.scene.image.Image;
import javafx.stage.Stage;

import java.net.URL;
import java.util.Objects;

public class JavaFXApp extends Application  {

    public static void main() {
        JavaFXApp.launch();
    }

    @Override
    public void start(Stage stage) throws Exception {

     //   URL mainFXML = getClass().getResource("/main.fxml");
     //   Objects.requireNonNull(mainFXML);
     //   Parent root = FXMLLoader.load(mainFXML);

        Hub hub = Hub.instance();

        PartitionedFile file = hub.get(PartitionedFile.class);

        Objects.requireNonNull(file);

        var root = new EditorCanvas(file);

        Scene scene = new Scene(root, 300, 300);



        stage.setTitle("Einsicht - 1s");
        stage.getIcons().add(new Image(getClass().getResourceAsStream("/einsicht-logo-v1.128.png")));
        stage.setScene(scene);

        stage.show();
    }
}
