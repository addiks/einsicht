package de.addiks.einsicht.versioning;

import java.nio.file.Path;

public class GitVersioning implements Versioning {
    private final Path projectRoot;
    private final Path metaFolder;

    public GitVersioning(Path projectRoot, Path metaFolder) {
        this.projectRoot = projectRoot;
        this.metaFolder = metaFolder;
    }

    @Override
    public String name() {
        return "Git";
    }

    @Override
    public Path projectRoot() {
        return projectRoot;
    }

    @Override
    public Path metaFolder() {
        return metaFolder;
    }

    @Override
    public String status() {
        return ""; // TODO
    }

    @Override
    public void openUI() {
        // "git --git-dir=" + metaFolder + " --work-tree=" + projectRoot + " gui"
    }
}
