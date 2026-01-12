package de.addiks.einsicht.filehandling;

import de.addiks.einsicht.filehandling.codings.MappedString;

public class RowColumnOffset extends RowColumn {
    private final long offset;

    public RowColumnOffset() {
        this(1,1,0);
    }

    public RowColumnOffset(RowColumn rowColumn, long offset) {
        this(rowColumn.row(), rowColumn.column(), offset);
    }

    public RowColumnOffset(int row, int column, long offset) {
        super(row, column);
        this.offset = offset;
    }

    public RowColumnOffset advance(MappedString code) {
        RowColumn rowColumn = super.advance(code);
        int processedLength = code.length();
        long offset = this.offset;
        offset += processedLength;
        return new RowColumnOffset(rowColumn, offset);
    }

    public long offset() {
        return offset;
    }

}
