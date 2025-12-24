package de.addiks.einsicht;

import java.io.File;
import java.io.IOException;
import java.lang.Runtime;
import java.nio.file.Files;
import java.nio.file.Path;

import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.security.NoSuchAlgorithmException;
import java.util.List;
import java.util.UUID;

import de.addiks.einsicht.filehandling.FileByLineNumberIndex;
import de.addiks.einsicht.filehandling.PartitionParser;
import de.addiks.einsicht.filehandling.PartitionedFile;
import de.addiks.einsicht.filehandling.writing.FileWriteStrategy;
import de.addiks.einsicht.filehandling.writing.WriteWholeFileDirectly;
import de.addiks.einsicht.languages.Language;
import de.addiks.einsicht.languages.LanguageSelector;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.versioning.Versioning;
import de.addiks.einsicht.versioning.VersioningSelector;
import de.addiks.einsicht.view.JavaFXThread;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import de.addiks.einsicht.view.widgets.EditorWindow;
import org.jspecify.annotations.Nullable;

public class Application {
    private static final Logger LOGGER = LogManager.getLogger();
    
    private final static MessageDigest sha256;
    static {
        try {
            sha256 = MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
    
    private static Application instance = null;
    
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

    private JavaFXThread javaFXThread = new JavaFXThread();
    

    public static void main(String[] argv) {
        try {
            Path filePath = null;
            if (argv.length > 1) {
                filePath = FileSystems.getDefault().getPath(argv[1]).toAbsolutePath();
            }


            Application.instance = new Application(filePath);
            return;
//        } catch (SystemExit exception) {
//            return 0;
        
     //   } catch (MessageBroker.FileAlreadyOpenOnOtherProcessException exception) {
     //       return;

        } catch (Exception exception) {
            LOGGER.error("Uncatched: {}", exception.getMessage(), exception);
            return;
        }
    }
    
    public static Application instance() {
        return Application.instance;
    }
    
    public Application(@Nullable Path filePath) throws IOException {
        instance = this;
        hub.setup(this);

        if (filePath == null) {
            UUID id = UUID.randomUUID();
            filePath = userStorageFolder().resolve("new-files/" + id);
            filePath.getParent().toFile().mkdirs();
            filePath.toFile().createNewFile();
        }

        this.filePath = filePath;

      //  window = new EditorWindow(hub);
        versioningSelector = new VersioningSelector(hub);

        openFile(filePath);

        // JavaFXApp.launch();
        javaFXThread.start();
        isReadyForInteraction = true;
    }

    public boolean isReadyForInteraction() {
        return isReadyForInteraction;
    }

    public Hub hub() {
        return hub;
    }

    public void openFile(Path filePath) throws IOException {
        this.filePath = filePath.toAbsolutePath();
        System.out.println(filePath);
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

    public Path userStorageFolder() {
        return Path.of(System.getProperty("user.home")).resolve(".local/share/addiks/Einsicht");
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
