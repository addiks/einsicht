package de.addiks.einsicht.view;

import de.addiks.einsicht.Hub;
import de.addiks.einsicht.filehandling.PartitionedFile;
import de.addiks.einsicht.view.widgets.EditorWindow;
import de.addiks.einsicht.view.widgets.TextCursor;
import javafx.application.Application;
import javafx.event.EventType;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;

import java.util.Objects;

public class JavaFXApp extends Application  {

    public static class JavaFXThread extends Thread {
        public void run() {
            JavaFXApp.main();
            TextCursor.shutdownAllCursors();
            de.addiks.einsicht.Application.instance().exit();
        }
    }

    private static void main() {
        JavaFXApp.launch();
    }

    @Override
    public void start(Stage stage) throws Exception {
        Hub hub = Hub.instance();

        PartitionedFile file = hub.get(PartitionedFile.class);
        Objects.requireNonNull(file);

        EditorWindow window = new EditorWindow(hub, file);
        Scene scene = new Scene(window, 300, 300);

        stage.setTitle("Einsicht - 1s");
        stage.getIcons().add(new Image(getClass().getResourceAsStream("/einsicht-logo-v1.128.png")));
        stage.setScene(scene);

        stage.addEventHandler(EventType.ROOT, window::processEvent);

        hub.register(window);
        hub.register(scene);
        hub.register(stage);

        stage.show();
    }
}
