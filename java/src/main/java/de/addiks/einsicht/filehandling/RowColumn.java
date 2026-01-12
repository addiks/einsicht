package de.addiks.einsicht.filehandling;

import de.addiks.einsicht.filehandling.codings.MappedString;

public class RowColumn {
    private final int row;
    private final int column;

    public RowColumn(int row, int column) {
        this.row = row;
        this.column = column;
    }

    public RowColumn advance(MappedString code) {
        int processedLength = code.length();
        int row = this.row;
        int column = this.column;
        row += code.substringCount("\n");
        if (code.contains("\n")) {
            column += processedLength - code.lastIndexOf("\n");
        } else {
            column += processedLength;
        }
        return new RowColumn(row, column);
    }

    public RowColumn nextRow() {
        return nextRow(1);
    }

    public RowColumn nextRow(int column) {
        return new RowColumn(row + 1, column);
    }

    public RowColumn nextColumn() {
        return new RowColumn(row, column + 1);
    }

    public int row() {
        return row;
    }

    public int column() {
        return column;
    }
}
