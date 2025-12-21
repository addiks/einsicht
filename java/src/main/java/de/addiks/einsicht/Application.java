package de.addiks.einsicht;

import java.io.IOException;
import java.lang.Runtime;
import java.nio.file.Files;
import java.nio.file.Path;

import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileSystems;
import java.security.NoSuchAlgorithmException;
import java.util.List;

import de.addiks.einsicht.languages.Language;
import de.addiks.einsicht.languages.LanguageSelector;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.versioning.Versioning;
import de.addiks.einsicht.versioning.VersioningSelector;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import de.addiks.einsicht.widgets.EditorWindow;

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
    private final EditorWindow window;
    private final VersioningSelector versioningSelector;
    
    private boolean isReadyForInteraction = false;
    private int textChangeCounter = 0;
    private MessageBroker messageBroker = null;
    private Language language = null;
    private Versioning versioning;
    private Object projectIndex;
    private List<ASTNode> tokens;
    private ASTRoot syntaxTree;
    
    private String fileContent = "";
    private Path filePath = null;
    private String hashOnDisk = "";
    private int lengthOnDisk = 0;
    

    public static int main(String[] argv) {
        try {
            Application.instance().run(argv);
            return 0;
//        } catch (SystemExit exception) {
//            return 0;
        
        } catch (MessageBroker.FileAlreadyOpenOnOtherProcessException exception) {
            return 0;

        } catch (Exception exception) {
            LOGGER.error("Uncatched: {}", exception.getMessage(), exception);
            return -1;
        }
    }
    
    public static Application instance() {
        if (Application.instance == null) {
            Application.instance = new Application();
        }
        return Application.instance;
    }
    
    public Application() {
        // setApplicationDisplayName("Einsicht - 1s");
        // setDesktopFileName("einsicht");
        hub.setup(this);
        reset();
        window = new EditorWindow(hub);
        versioningSelector = new VersioningSelector(hub);
    }
    
    public void reset() {
        
    }
    
    public void run(String[] argv) throws IOException, MessageBroker.FileAlreadyOpenOnOtherProcessException {
        Path filePath = null;
        if (argv.length > 1) {
            filePath = FileSystems.getDefault().getPath(argv[1]).toAbsolutePath();
        }
        
        if (filePath != null) {
            openFile(filePath);
        } else {
            reset();
            window.onFileClosed();
        }
        
        window.show();
        isReadyForInteraction = true;
    }
    
    public boolean isReadyForInteraction() {
        return isReadyForInteraction;
    }
    
    public void closeFile() {
        reset();
        if (messageBroker != null) {
            messageBroker.close();
        }
        hub.notify(FileAccess.class, "closeFile");
        LOGGER.info("Closed file");
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
        
        fileContent = Files.readString(filePath, StandardCharsets.UTF_8);
        LOGGER.info("Read %d bytes".formatted(fileContent.length()));
        
        syntaxTree = null;
        if (language != null) {
          //  Language.ParseResult parseResult = language.parse(fileContent, null, null, null);
          //  syntaxTree = parseResult.previousAST();
          //  tokens = parseResult.previousTokens();
        }
        
        versioning = versioningSelector.selectVersioningFor(filePath);
        
        projectIndex = null;
        if (versioning != null) {
            // projectIndex = new ProjectIndex(versioning.metaFolder() + "/einsicht.db");
        }
        
        hashOnDisk = md5(fileContent);
        lengthOnDisk = fileContent.length();
        
        // document.setPlainText(filePath);
        
        window.onFileOpened();
        hub.notify(FileAccess.class, "openFile");
    }
    
    public void saveFile() {
        try {
         //   if (syntaxTree != null) {
         //       fileContent = syntaxTree.reconstructCode();
         //   }
            Files.writeString(filePath, fileContent);
            updateProjectIndex();
            hashOnDisk = md5(fileContent);
            lengthOnDisk = fileContent.length();
        } catch (IOException exception) {
            LOGGER.error("Error saving file to disk: {}", exception.getMessage(), exception);
        }
    }
    
    public void saveFileAs(Path filePath) {
    
    }
    
    public boolean isModified() {
        if (fileContent.length() != lengthOnDisk) {
            return true;
        }
        return !md5(fileContent).equals(hashOnDisk);
    }
    
    public Path filePath() {
        return filePath;
    }
    
    public String fileContent() {
        return fileContent;
    }
    
    private void updateProjectIndex() {
    
    }
    
    private void onDocumentContentsChanged() {
    
    }
    
    private void reparseFile() {
    
    }
    
    private void checkAutocompleteTrigger() {
        
    }
    
    public void showOpenFilePicker() {
        String folderPath = null;
        // if 
    }
    
    public void newFile() {
        String cmdLine = String.format(
                "nohup %s > %s.log 2>&1 &",
                bashScript(),
                bashScript()
        );

        try {
            Runtime.getRuntime().exec(cmdLine);
        } catch (IOException e) {
            LOGGER.error("Could not open new empty file using '{}': {}", cmdLine, e.getMessage(), e);
        }
    }
    
    public String fileNameDescription() {
        if (filePath == null) {
            return "[no file]";
        } else {
            return filePath.getFileName().toString();
        }
    }
    
    private String bashScript() {
        return baseDir() + "/bin/1s.sh";
    }
    
    public String baseDir() {
        return "";
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
