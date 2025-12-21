package de.addiks.einsicht.filehandling;

import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.languages.Language;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;

import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;

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
            MappedString dataInPartition,
            long startingOffset
    ) throws IOException {
        return new ParsedPartition(parse(dataInPartition, startingOffset), this);
    }

    @Override
    public FileTransaction.Partition combine(FileTransaction.Partition first, FileTransaction.Partition second) {

          Token preceedingToken = null;
          if (first instanceof ParsedPartition firstParsedPartition) {
              preceedingToken = firstParsedPartition.syntaxTree().lastToken();
          }

          Token followingToken = null;
          if (second instanceof ParsedPartition secondParsedPartition) {
              followingToken = secondParsedPartition.syntaxTree().firstToken();
          }
    }

    public ASTRoot parse(
            MappedString originalContent,
            long startingOffset
    ) throws IOException {

        Language.ParseResult parsed = language.parse(
                originalContent,
                file.toPath(),
                lineIndex.lineAtOffset(startingOffset),
                columnAtOffset(startingOffset),
                startingOffset
        );

        return parsed.previousAST();
    }

    private int columnAtOffset(long offset) throws IOException {
        try (RandomAccessFile raf = new RandomAccessFile(file, "r")) {
            long currentOffset = offset;
            while (currentOffset > 0) {
                raf.seek(currentOffset);
                byte b =  raf.readByte();
                currentOffset--;
                if (b == (byte) 0x0A) {
                    return (int) (offset - currentOffset);
                }
            }
        }
        return (int) offset;
    }

}
