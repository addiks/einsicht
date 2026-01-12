package de.addiks.einsicht.view.widgets.abstract_syntax_tree;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import javafx.scene.layout.HBox;
import javafx.scene.layout.Region;
import javafx.scene.shape.Rectangle;
import org.eclipse.jdt.annotation.NonNullByDefault;
import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

@NonNullByDefault
public class ASTRowWidget extends HBox {
    private final ASTRowWidgetContainer container;
    private final int lineNumber;
    private final List<ASTWidget<?>> content;
    private final List<ASTCharacterWidget> characters;

    public ASTRowWidget(
            ASTRowWidgetContainer container,
            int lineNumber,
            List<ASTWidget<?>> content,
            @Nullable List<ASTCharacterWidget> characters
    ) {
        if (characters == null) {
            characters = new ArrayList<>();
        }
        this.container = container;
        this.lineNumber = lineNumber;
        this.content = content;
        this.characters = characters;

//        setHeight(16.0);

        getChildren().add(new Rectangle(0, 16.0));

        for (ASTWidget<?> astWidget : content) {
            getChildren().add(astWidget);
        }
    }

    public ASTRowWidgetContainer container() {
        return container;
    }

    public List<ASTWidget<?>> content() {
        return content;
    }

    public List<ASTCharacterWidget> characters() {
        return characters;
    }

    public @Nullable ASTCharacterWidget characterWidgetAt(int column) {
        for (ASTWidget<?> astWidget : content) {

        }
        return null;
    }

    public ASTRowWidget merge(ASTRowWidget other) {
        if (container != other.container) {
            throw new IllegalArgumentException("Cannot merge AST row widgets with different containers!");
        }
        if (lineNumber != other.lineNumber) {
            throw new IllegalArgumentException("Cannot merge AST row widgets for different rows!");
        }
        List<ASTWidget<?>> newContent = new ArrayList<>();
        newContent.addAll(content);
        newContent.addAll(other.content);

        List<ASTCharacterWidget> newCharacters = new ArrayList<>();
        newCharacters.addAll(characters);
        newCharacters.addAll(other.characters);

        return new ASTRowWidget(container, lineNumber, newContent, newCharacters);
    }

    public @Nullable Token tokenAtColumn(int column) {
        for (ASTWidget<?> astWidget : content) {
            Token token = astWidget.node().firstToken();
            while (token != null && token.end().column() < column) {
                token = token.next();
            }
            if (token != null && token.column() <= column && token.end().column() >= column) {
                return token;
            }
        }
        return null;
    }

    public int lineNumber() {
        return lineNumber;
    }

    public @Nullable ASTCharacterWidget firstCharacter() {
        if (!characters.isEmpty()) {
            return characters.getFirst();
        }
        return null;
    }
}
