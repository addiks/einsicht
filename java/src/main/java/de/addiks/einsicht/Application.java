package de.addiks.einsicht;

import java.io.File;
import java.io.IOException;
import java.lang.Runtime;
import java.nio.file.Path;

import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.security.NoSuchAlgorithmException;
import java.time.Clock;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.FormatStyle;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

import de.addiks.einsicht.filehandling.FileByLineNumberIndex;
import de.addiks.einsicht.filehandling.PartitionParser;
import de.addiks.einsicht.filehandling.PartitionedFile;
import de.addiks.einsicht.filehandling.writing.FileWriteStrategy;
import de.addiks.einsicht.filehandling.writing.WriteWholeFileDirectly;
import de.addiks.einsicht.languages.Language;
import de.addiks.einsicht.languages.LanguageSelector;
import de.addiks.einsicht.versioning.Versioning;
import de.addiks.einsicht.versioning.VersioningSelector;
import de.addiks.einsicht.view.JavaFXApp;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import org.jspecify.annotations.Nullable;

import javax.swing.text.DateFormatter;

public class Application {
    private static final Logger LOGGER = LogManager.getLogger();
    private static final DateTimeFormatter dateFormatter = DateTimeFormatter.ofLocalizedDateTime(FormatStyle.MEDIUM);
    
    private final static MessageDigest sha256;
    static {
        try {
            sha256 = MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
    
    private static Application instance = null;

    private final Clock clock;
    private final Hub hub = new Hub();
    private final VersioningSelector versioningSelector;
    
    private boolean isReadyForInteraction = false;
    private MessageBroker messageBroker = null;
    private Language language = null;
    private PartitionedFile partitionedFile;
    private FileByLineNumberIndex lineIndex;
    private Versioning versioning;
    private Object projectIndex;

    private Path filePath = null;

    private JavaFXApp.JavaFXThread javaFXThread = new JavaFXApp.JavaFXThread();
    

    public static void main(String[] argv) {
        try {
            Path filePath = null;
            if (argv.length > 1) {
                filePath = FileSystems.getDefault().getPath(argv[1]).toAbsolutePath();
            }

            Application.instance = new Application(filePath, Clock.system(ZoneId.systemDefault()));
            Application.instance().run();

        } catch (Exception exception) {
            LOGGER.error("Uncatched: {}", exception.getMessage(), exception);
        }
    }
    
    public static Application instance() {
        return Application.instance;
    }
    
    public Application(@Nullable Path filePath, Clock clock) {
        instance = this;
        hub.setup(this);
        this.clock = clock;
        this.filePath = filePath;
        versioningSelector = new VersioningSelector(hub);
    }

    public void run() throws IOException {
        if (filePath == null) {
            filePath = folderForUnnamedFiles().resolve(newUnnamedFileName());
            filePath.getParent().toFile().mkdirs();
            filePath.toFile().createNewFile();
        }

        openFile(filePath);

        // JavaFXApp.launch();
        javaFXThread.start();
        isReadyForInteraction = true;
    }

    public void exit() {
        saveFile();
        File file = filePath.toFile();
        if (file.length() == 0) {
            file.delete();
        }
        System.exit(0);
    }

    private static String newUnnamedFileName() {
        // TODO: These language names are probably mostly wrong
        String wordUnnamed = switch (Locale.getDefault().getDisplayLanguage()) {
            case "Deutsch" -> "Datei ohne Namen von %s";
            case "French" -> "Fichier sans nom du %s";
            case "Spanish" -> "Archivo sin nombre del %s";
            case "Italian" -> "File senza nome del %s";
            case "Chinese" -> "的未命名文件 %s";
            case "Japanese" -> "名前のないファイル %s";
            case "Ukranian" -> "Файл без назви з %s";
            default -> "Unnamed file at %s";
        };
        return wordUnnamed.formatted(dateFormatter.format(LocalDateTime.now()));
    }

    public boolean isReadyForInteraction() {
        return isReadyForInteraction;
    }

    public Hub hub() {
        return hub;
    }

    public void openFile(Path filePath) throws IOException {
        this.filePath = filePath.toAbsolutePath();
        // Log.setPrefix(self.fileNameDescription() + ' - ')
        try {
            messageBroker = new MessageBroker(hub);
        } catch (Exception e) {
            LOGGER.error("Could not create DBUS mesage broker: {}", e.getMessage(), e);
        }
        
        LanguageSelector selector = new LanguageSelector(hub);
        language = selector.selectForFilePath(this.filePath);

        File file = filePath.toFile();
        FileByLineNumberIndex lineIndex = new FileByLineNumberIndex(file);
        hub.register(lineIndex);

        PartitionParser partitionParser = new PartitionParser(file, language, lineIndex);
        partitionedFile = new PartitionedFile(file, partitionParser);
        hub.register(partitionedFile);
        
        versioning = versioningSelector.selectVersioningFor(filePath);
        
        projectIndex = null;
        if (versioning != null) {
            // projectIndex = new ProjectIndex(versioning.metaFolder() + "/einsicht.db");
        }

     //   hub.notify(FileAccess.class, "openFile");
    }
    
    public void saveFile() {
        try {
            FileWriteStrategy.FileWriteStatus status = determineBestWritingStrategy().writeFile(partitionedFile);
            updateProjectIndex();
        } catch (IOException exception) {
            LOGGER.error("Error saving file to disk: {}", exception.getMessage(), exception);
        }
    }
    
    public void saveFileAs(Path filePath) {
        try {
            FileWriteStrategy.FileWriteStatus status = determineBestWritingStrategy().writeFile(partitionedFile, filePath);
            updateProjectIndex();

            String cmdLine = String.format("nohup %s \"%s\" > %s.log 2>&1 &", bashScript(), filePath, bashScript());

            Runtime.getRuntime().exec(cmdLine);


        } catch (IOException exception) {
            LOGGER.error("Error saving file to disk: {}", exception.getMessage(), exception);
        }
    }
    
    public boolean isModified() {
        return partitionedFile.isModified();
    }
    
    public Path filePath() {
        return filePath;
    }

    private FileWriteStrategy determineBestWritingStrategy() {
        // TODO
        return new WriteWholeFileDirectly(); // if file is small enough to write all at once
        // return new WritePartitionsShiftEnd(); // if file is too big and NOT enough space for a separate file is free
        // return new WriteToSeparateFile(); // if file is too big and enough space is free
        // Also: Maybe the user should be asked what behaviour is desired?
    }

    private void updateProjectIndex() {
    
    }
    
    private void onDocumentContentsChanged() {
    
    }

    public void showOpenFilePicker() {
        String folderPath = null;
        // if 
    }
    
    public void newFile() {
        String cmdLine = String.format("nohup %s > %s.log 2>&1 &", bashScript(), bashScript());

        try {
            Runtime.getRuntime().exec(cmdLine);
        } catch (IOException e) {
            LOGGER.error("Could not open new empty file using '{}': {}", cmdLine, e.getMessage(), e);
        }
    }
    
    public String fileNameDescription() {
        return filePath.getFileName().toString();
    }
    
    private String bashScript() {
        return baseDir() + "/bin/1s.sh";
    }
    
    public String baseDir() {
        return "";
    }

    public Path folderForUnnamedFiles() {
        String osName = System.getProperty("os.name");
        Path userHome = Path.of(System.getProperty("user.home"));
        for (String desktopSubDir : List.of(
                "Schreibtisch", "Arbeitsfläche", "Desktop", "DeskTop", "Bureau", "Escritorio", "Scrivania",
                "Área de Trabalho", "Bureaublad", "Skrivebord", "Skrivbord", "Työpöytä", "Pulpit", "Plocha",
                "Стільниця", "Робочий стіл", "Επιφάνεια εργασίας", "Masaüstü", "デスクトップ", "桌面", "바탕화면"
        )) {
            Path desktopDir = userHome.resolve(desktopSubDir);
            if (desktopDir.toFile().exists()) {
                return desktopDir;
            }
        }
        if (osName.contains("Windows")) {
            return userHome.resolve("AppData\\Roaming\\addiks\\Einsicht");
        }
        if (osName.contains("Mac OS")) {
            return userHome.resolve("Library/Application Support/Einsicht");
        }
        // TODO: Try env-var XDG_DESKTOP_DIR
        // TODO: Read ~/.config/user-dirs.dirs
        return userHome.resolve(".local/share/addiks/Einsicht");
    }

    public static String md5(String input) {
        return bytesToHex(sha256.digest(input.getBytes(StandardCharsets.UTF_8)));
    }
    
    private static String bytesToHex(byte[] hash) {
        StringBuilder hexString = new StringBuilder(2 * hash.length);
        for (byte b : hash) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) {
                hexString.append('0');
            }
            hexString.append(hex);
        }
        return hexString.toString();
    }
}
