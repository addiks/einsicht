package de.addiks.einsicht.filehandling;

import de.addiks.einsicht.languages.Language;
import de.addiks.einsicht.tokens.Token;
import org.jspecify.annotations.Nullable;

import java.io.File;
import java.io.IOException;

public class PartitionParser implements FileTransaction.Partition.Factory {
    private final File file;
    private final FileByLineNumberIndex lineIndex;
    private final Language language;

    public PartitionParser(File file, Language language) throws IOException {
        this.file = file;
        this.language = language;
        lineIndex = new FileByLineNumberIndex(file);
    }

    @Override
    public FileTransaction.Partition create(
            byte[] originalContent,
            FileTransaction.@Nullable Partition preceedingPartition,
            FileTransaction.@Nullable Partition followingPartition
    ) {
        Token preceedingToken = null;
        if (preceedingPartition instanceof ParsedPartition parsedPreceedingPartition) {
            preceedingToken = parsedPreceedingPartition.syntaxTree().lastToken();
        }

        Token followingToken = null;
        if (followingPartition instanceof ParsedPartition parsedFollowingPartition) {
            followingToken = parsedFollowingPartition.syntaxTree().firstToken();
        }

        Language.ParseResult parsed = language.parse(
                new String(originalContent),
                file.toPath(),
                preceedingToken,
                followingToken
        );

        return new ParsedPartition(
                parsed.previousAST()
        );
    }
}
