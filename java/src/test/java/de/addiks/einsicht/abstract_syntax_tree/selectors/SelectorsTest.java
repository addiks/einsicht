package de.addiks.einsicht.abstract_syntax_tree.selectors;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.languages.Language;
import org.junit.jupiter.api.Test;

import java.nio.file.Path;
import java.util.ArrayList;
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
                                new ASTNode(language, "", 0,0,0, "bar")
                        ), "baz"),
                        new ASTBranch(List.of(
                                new ASTNode(language, "", 0,0,0, "bar")
                        ), "foo")
                ), "foo"),
                new ASTBranch(List.of(
                    new ASTNode(language, "", 0,0,0, "foo")
                ), "bar"),
                new ASTBranch(List.of(
                        new ASTNode(language, "", 0,0,0, "bar")
                ), "foo")
        ), Path.of("some-file-path"));

        ASTSelector selector = ASTSelector.of("foo/bar");

        List<ASTNode> results = selector.selectIn(root);

        assertEquals(2, results.size());
        assertEquals("bar", results.getFirst().grammarKey());
        assertEquals("foo", results.getFirst().getParent().grammarKey());
        assertEquals("bar", results.getLast().grammarKey());
        assertEquals("foo", results.getLast().getParent().grammarKey());
    }

}
