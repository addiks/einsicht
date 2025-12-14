package de.addiks.einsicht.tokens;

public class ConsumableString {
    private final String text;
    private final int length;
    private int position = 0;

    public ConsumableString(String string) {
        this.text = string;
        this.length = string.length();
    }

    public String get() {
        return text.substring(position);
    }

    public char charAt(int at) {
        return text.charAt(position + at);
    }

    public boolean startsWith(String prefix) {
        return get().startsWith(prefix);
    }

    public String substring(int begin) {
        return get().substring(begin);
    }

    public String substring(int begin, int end) {
        return get().substring(begin, end);
    }

    public int length() {
        return length - position;
    }

    public String consume(int length) {
        position += length;
        return text.substring(position - length, position);
    }

    public String consume(String toConsume) {
        int toConsumeLength = toConsume.length();
        assert toConsume.equals(substring(0, toConsumeLength));
        return consume(toConsumeLength);
    }

    public String consumed(int lengthBack) {
        return text.substring(position - lengthBack, lengthBack);
    }
}
