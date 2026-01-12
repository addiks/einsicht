package de.addiks.einsicht.abstract_syntax_tree.selectors;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import de.addiks.einsicht.filehandling.RowColumnOffset;
import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.languages.Language;
import org.junit.jupiter.api.Test;

import java.nio.file.Path;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

public class SelectorsTest {

    @Test
    public void shouldSelectNodes() {

        Language language = mock(Language.class);



        ASTRoot root = new ASTRoot(List.of(
                new ASTBranch(List.of(
                        new ASTBranch(List.of(
                                new ASTLeaf(language, "bar")
                        ), "baz"),
                        new ASTBranch(List.of(
                                new ASTLeaf(language, "bar")
                        ), "foo")
                ), "foo"),
                new ASTBranch(List.of(
                    new ASTLeaf(language, "foo")
                ), "bar"),
                new ASTBranch(List.of(
                        new ASTLeaf(language, "bar")
                ), "foo")
        ), Path.of("some-file-path"));

        ASTSelector selector = ASTSelector.of("foo/bar");

        List<ASTNode> results = selector.selectIn(root);

        assertEquals(2, results.size());
        assertEquals("bar", results.getFirst().grammarKey());
        assertEquals("foo", results.getFirst().parent().grammarKey());
        assertEquals("bar", results.getLast().grammarKey());
        assertEquals("foo", results.getLast().parent().grammarKey());
    }

    public static class ASTLeaf extends ASTNode {

        public ASTLeaf(Language language, String grammarKey) {
            super(language, new RowColumnOffset(), grammarKey);
        }

        @Override
        public Token firstToken() {
            return null;
        }

        @Override
        public Token lastToken() {
            return null;
        }

        @Override
        public void collectTokens(List<Token> tokens) {

        }

        @Override
        public MappedString.Builder newStringBuilder() {
            return null;
        }

        @Override
        public void reconstructCode(MappedString.Builder codeBuilder) {

        }
    }

}
