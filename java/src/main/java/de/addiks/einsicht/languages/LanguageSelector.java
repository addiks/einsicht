package de.addiks.einsicht.languages;

import de.addiks.einsicht.Hub;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class LanguageSelector {
    private static final Logger log = LoggerFactory.getLogger(LanguageSelector.class);
    private final Hub hub;

    public LanguageSelector(Hub hub) {
        this.hub = hub;
    }

    public Language selectForFilePath(Path filePath) throws IOException {
        Language language = null;

        String mimeType = Files.probeContentType(filePath);
        if (mimeType != null) {
            if (mimeType.equals("text/x-python")) {
                language = new PythonLanguage(hub);

            } else if (mimeType.equals("application/x-python-code")) {
                // Python bytecode

            } else if (mimeType.equals("text/php")) {

            }

            if (language == null) {
                log.warn("Unknown mime-type '{}'!", mimeType);
            }
        }

        if (language == null) {
            if (filePath.endsWith(".md")) {

            } else if (filePath.endsWith(".java")) {
                language = new JavaLanguage(hub);
            }
        }

        if (language == null) {
            log.warn("Could not determine lanugage for file '{}'!", filePath);
            language = new UnknownLanguage(hub);
        }

        log.info("Determined language of '{}' to be {}.", filePath, language.name());
        return language;
    }


}
