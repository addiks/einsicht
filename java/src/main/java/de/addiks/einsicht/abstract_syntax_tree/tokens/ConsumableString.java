package de.addiks.einsicht.abstract_syntax_tree.tokens;

import de.addiks.einsicht.filehandling.codings.MappedString;

public class ConsumableString {
    private final MappedString text;
    private final int length;
    private int position = 0;

    public ConsumableString(MappedString string) {
        this.text = string;
        this.length = string.length();
    }

    public MappedString get() {
        return text.substring(position);
    }

    public char charAt(int at) {
        return text.charAt(position + at);
    }

    public boolean startsWith(String prefix) {
        return get().startsWith(prefix);
    }

    public MappedString substring(int begin) {
        return get().substring(begin);
    }

    public MappedString substring(int begin, int end) {
        return get().substring(begin, end);
    }

    public int length() {
        return length - position;
    }

    public MappedString consume(int length) {
        position += length;
        return text.substring(position - length, position);
    }

    public MappedString consume(String toConsume) {
        int toConsumeLength = toConsume.length();
        assert toConsume.equals(substring(0, toConsumeLength));
        return consume(toConsumeLength);
    }

    public MappedString consumed(int lengthBack) {
        return text.substring(position - lengthBack, lengthBack);
    }
}
