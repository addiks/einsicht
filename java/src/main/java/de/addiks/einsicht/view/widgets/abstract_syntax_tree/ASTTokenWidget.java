package de.addiks.einsicht.view.widgets.abstract_syntax_tree;

import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import de.addiks.einsicht.abstract_syntax_tree.tokens.Token;
import de.addiks.einsicht.filehandling.RowColumn;
import de.addiks.einsicht.filehandling.codings.DecodedCharacter;
import de.addiks.einsicht.filehandling.codings.MappedString;
import org.eclipse.jdt.annotation.NonNullByDefault;
import org.eclipse.jdt.annotation.Nullable;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@NonNullByDefault
public class ASTTokenWidget extends ASTWidget<Token> {
    private final List<ASTCharacterWidget> characterWidgets = new ArrayList<>();

    public ASTTokenWidget(Token token) {
        super(token);
        readToken(token);
    }

    public ASTTokenWidget(Token token, RowColumn from, RowColumn to) {
        super(token, from, to);
        readToken(token);
    }

    public static ASTTokenWidget of(Token token) {
        return new ASTTokenWidget(token);
    }

    public @Nullable ASTCharacterWidget firstCharacter() {
        return characterWidgets.getFirst();
    }

    public @Nullable ASTCharacterWidget lastCharacter() {
        return characterWidgets.getLast();
    }

    public Map<Integer, ASTWidget<Token>> separateByRows() {
        Token token = node();
        RowColumn start = token.position();
        RowColumn end = token.end();

        if (start.row() == end.row()) {
            return Map.of(start.row(),this);
        }

        MappedString code = token.reconstructCode();
        Map<Integer, ASTWidget<Token>> rows = new HashMap<>();
        RowColumn rowStart = start;
        RowColumn current = start;
        for (int offset = 0; offset < code.length(); offset++) {
            char character = code.charAt(offset);
            if (character == '\n') {
                rows.put(current.row(), new ASTTokenWidget(token, rowStart, current));
                rowStart = current.nextRow();
                current = rowStart;
            } else {
                current = current.nextColumn();
            }
        }

        return rows;
    }

    @Override
    public ASTWidget<Token> merge(ASTWidget<Token> other) {


        return null;
    }

    private void readToken(Token token) {
        ASTCharacterWidget previous = null;
        for (DecodedCharacter character : token.code()) {
            var characterWidget = new ASTCharacterWidget(this, character, previous);
            characterWidgets.add(characterWidget);
            previous = characterWidget;
        }
    }

    public List<ASTCharacterWidget> characters() {
        return characterWidgets;
    }
}
