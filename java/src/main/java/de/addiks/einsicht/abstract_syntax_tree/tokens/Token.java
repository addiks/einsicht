package de.addiks.einsicht.abstract_syntax_tree.tokens;

import de.addiks.einsicht.filehandling.RowColumnOffset;
import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.languages.Language;
import de.addiks.einsicht.abstract_syntax_tree.ASTNode;
import org.jspecify.annotations.Nullable;

import java.util.List;

public class Token extends ASTNode {
    private final String tokenName;
    private final MappedString code;
    private final @Nullable TokenMatcher matcher;

    private @Nullable Token next;
    private @Nullable Token previous;

    private EndReference first;
    private EndReference last;

    public Token(Language language, String tokenName, MappedString code, RowColumnOffset position, TokenMatcher matcher) {
        this(language, tokenName, code, position, null, matcher);
    }

    public Token(
            Language language,
            String tokenName,
            MappedString code,
            RowColumnOffset position,
            Token previous,
            @Nullable TokenMatcher matcher
    ) {
        super(language, position, "token", null, List.of());
        this.code = code;
        this.tokenName = tokenName;
        this.matcher = matcher;

        if (previous != null) {
            previous = previous.last();
            this.previous = previous;
            first = previous.first;
            last = previous.last;
            last.set(this);

        } else {
            first = new EndReference(this);
            last = new EndReference(this);
        }
    }

    public void prependToChain(Token other) {
        other.appendToChain(this);
    }

    public void appendToChain(Token other) {
        if (isRelatedTo(other)) {
            throw new IllegalArgumentException("Cannot append token-chain to self!");
        }

        Token localFirst = first();
        Token remoteLast = other.last();

        remoteLast.next = localFirst;
        localFirst.previous = remoteLast;

        first.set(other.first.get());
        other.last.set(last.get());
    }

    public void insertIntoChainBefore(Token other) {
        if (isRelatedTo(other)) {
            throw new IllegalArgumentException("Cannot insert token-chain into self!");
        }

        Token othersPrevious = other.previous;
        if (othersPrevious == null) {
            prependToChain(other);

        } else {
            Token localFirst = first();
            Token localLast = last();

            othersPrevious.next = localFirst;
            localFirst.previous = othersPrevious;

            other.previous = localLast;
            localLast.next = other;

            first.defer(other.first);
            last.defer(other.last);
        }
    }

    public void insertIntoChainAfter(Token other) {
        if (isRelatedTo(other)) {
            throw new IllegalArgumentException("Cannot insert token-chain into self!");
        }

        Token otherNext = other.next;
        if (otherNext == null) {
            appendToChain(other);

        } else {
            Token localFirst = first();
            Token localLast = last();

            otherNext.previous = localLast;
            localLast.next = otherNext;

            other.next = localFirst;
            localFirst.previous = other;

            first.defer(other.first);
            last.defer(other.last);
        }
    }

    public void removeSelfFromChain() {
        if (next != null) {
            next.previous = previous;
        }
        if (previous != null) {
            previous.next = next;
        }
        previous = null;
        next = null;
        first = new EndReference(this);
        last = new EndReference(this);
    }

    public void replaceWith(Token replacement) {
        replacement.first().previous = previous;
        replacement.last().next = next;
        previous = null;
        next = null;
        // TODO
    }

    public void removeFromChainFromThisTo(Token lastExtracted) {
        // TODO
    }

    public Token first() {
        return first.get();

        // Token first = this;
        // while (first.previous != null) {
        //     first = first.previous;
        // }
        // return first;
    }

    public @Nullable Token previous() {
        return previous;
    }

    public @Nullable Token next() {
        return next;
    }

    public boolean hasNext() {
        return next != null;
    }

    public Token last() {
        return last.get();

        // Token last = this;
        // while (last.next != null) {
        //     last = last.next;
        // }
        // return last;
    }

    public boolean isRelatedTo(Token other) {
        return first.get() == other.first.get();

        // for (Token related = first(); related != null; related = related.next) {
        //     if (related == other) {
        //         return true;
        //     }
        // }
        // return false;
    }

    public String tokenName() {
        return tokenName;
    }

    @Override
    public Token firstToken() {
        return this;
    }

    @Override
    public Token lastToken() {
        return this;
    }

    @Override
    public void collectTokens(List<Token> tokens) {
        for (ASTNode prepended : prepended()) {
            tokens.addAll(prepended.collectTokens());
        }
        tokens.add(this);
        for (ASTNode appended : appended()) {
            tokens.addAll(appended.collectTokens());
        }
    }

    @Override
    public MappedString.Builder newStringBuilder() {
        return code.newBuilder();
    }

    @Override
    public void reconstructCode(MappedString.Builder codeBuilder) {
        codeBuilder.append(code);
    }

    /** Datastructure optimized to shorten the path to find the first & last Tokens in any Token-chain. */
    private class EndReference {
        public @Nullable Token end;
        public @Nullable EndReference deferred;

        public EndReference(Token end) {
            this.end = end;
        }

        public void set(Token end) {
            if (deferred != null) {
                while (deferred.deferred != null) {
                    deferred = deferred.deferred;
                }
                deferred.set(end);
            } else {
                this.end = end;
            }
        }

        public void defer(EndReference reference) {
            while (reference.deferred != null) {
                reference = reference.deferred;
            }
            deferred = reference;
            end = null;
        }

        public @Nullable Token get() {
            if (end != null) {
                return end;
            } else if (deferred != null) {
                while (deferred.deferred != null) {
                    deferred = deferred.deferred;
                }
                return deferred.get();
            }
            return null;
        }
    }

}
