package de.addiks.einsicht.view.widgets.abstract_syntax_tree;

import de.addiks.einsicht.filehandling.codings.DecodedCharacter;
import de.addiks.einsicht.filehandling.codings.MappedString;
import javafx.scene.control.Label;
import org.jspecify.annotations.Nullable;

public class ASTCharacterWidget extends Label {
    private final ASTTokenWidget parent;
    private final DecodedCharacter character;

    private @Nullable ASTCharacterWidget previous;
    private @Nullable ASTCharacterWidget next;

    public ASTCharacterWidget(ASTTokenWidget parent, DecodedCharacter character, @Nullable ASTCharacterWidget previous) {
        super(character.toString());
        this.parent = parent;
        this.character = character;
        this.previous = previous;
        if (previous != null) {
            previous.next = this;
            this.layoutXProperty().bind(previous.layoutXProperty().add(this.widthProperty()));
        }
    }

    public ASTTokenWidget parent() {
        return parent;
    }

    public DecodedCharacter character() {
        return character;
    }

  //  public void setNext(@Nullable ASTCharacterWidget next) {
  //      if (this.next != next) {
  //          if (this.next != null) {
  //              this.next.layoutXProperty().unbind();
  //          }
  //          this.next = next;
  //          if (next != null) {
  //              this.next.layoutXProperty().bind(this.layoutXProperty().add(next.widthProperty()));
  //          }
  //      }
  //  }
//
  //  public void setPrevious(@Nullable ASTCharacterWidget previous) {
//
  //  }

    public @Nullable ASTCharacterWidget previous() {
        return previous;
    }

    public @Nullable ASTCharacterWidget next() {
        return next;
    }
}
