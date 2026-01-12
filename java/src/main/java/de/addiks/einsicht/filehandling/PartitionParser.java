package de.addiks.einsicht.filehandling;

import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.languages.Language;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import org.eclipse.jdt.annotation.NonNullByDefault;

import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.ArrayList;
import java.util.List;

@NonNullByDefault
public class PartitionParser implements PartitionedFile.Partition.Factory {
    private final File file;
    private final FileByLineNumberIndex lineIndex;
    private final Language language;

    public PartitionParser(File file, Language language, FileByLineNumberIndex lineIndex) {
        this.file = file;
        this.language = language;
        this.lineIndex = lineIndex;
    }

    public PartitionParser(File file, Language language) throws IOException {
        this(file, language, new FileByLineNumberIndex(file));
    }

    @Override
    public ParsedPartition create(
            MappedString dataInPartition,
            long startingOffset
    ) throws IOException {
        return new ParsedPartition(parse(dataInPartition, startingOffset), this);
    }

    @Override
    public ParsedPartition combine(PartitionedFile.Partition first, PartitionedFile.Partition second) {
        if (!(first instanceof ParsedPartition firstParsedPartition)) {
            throw new IllegalArgumentException("PartitionParser is incompatible with %s".formatted(
                    first.getClass().getName()
            ));
        }
        if (!(second instanceof ParsedPartition secondParsedPartition)) {
            throw new IllegalArgumentException("PartitionParser is incompatible with %s".formatted(
                    second.getClass().getName()
            ));
        }
        ASTRoot firstAST = firstParsedPartition.syntaxTree();
        ASTRoot secondAST = secondParsedPartition.syntaxTree();

        Token firstLastToken = firstAST.lastToken();
        Token secondFirstToken = secondAST.firstToken();

        MappedString.Builder combinedCodeBuilder = firstLastToken.newStringBuilder();
        combinedCodeBuilder.append(firstLastToken.code());
        combinedCodeBuilder.append(secondFirstToken.code());

        List<Token> combinedTokens = language.lex(
                combinedCodeBuilder.build(),
                firstLastToken.position()
        );

        List<Token> allTokens = new ArrayList<>();
        for (Token token : firstAST.collectTokens()) {
            if (token != firstLastToken) {
                allTokens.add(token);
            }
        }
        allTokens.addAll(combinedTokens);
        for (Token token : secondAST.collectTokens()) {
            if (token != secondFirstToken) {
                allTokens.add(token);
            }
        }

        Language.ParseResult parseResult = language.parse(allTokens, file.toPath());

        return new ParsedPartition(parseResult.ast(), this);
    }

    public ASTRoot parse(MappedString originalContent, long startingOffset) throws IOException {
        Language.ParseResult parsed = language.parse(
                originalContent,
                file.toPath(),
                new RowColumnOffset(
                        lineIndex.lineAtOffset(startingOffset),
                        columnAtOffset(startingOffset),
                        startingOffset
                )
        );

        return parsed.ast();
    }

    public FileByLineNumberIndex lineIndex() {
        return lineIndex;
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
