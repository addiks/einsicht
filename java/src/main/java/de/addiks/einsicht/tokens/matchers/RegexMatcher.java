package de.addiks.einsicht.tokens.matchers;

import de.addiks.einsicht.tokens.ConsumableString;
import de.addiks.einsicht.tokens.TokenDef;
import de.addiks.einsicht.tokens.TokenMatcher;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class RegexMatcher extends TokenMatcher {
    private final Pattern pattern;
    private final String tokenName;
    private final int groupNo;

    public RegexMatcher(Pattern pattern, String tokenName) {
        this(pattern, tokenName, 0);
    }

    public RegexMatcher(Pattern pattern, String tokenName, int groupNo) {
        this.pattern = pattern;
        this.tokenName = tokenName;
        this.groupNo = groupNo;
    }

    @Override
    public TokenDef lexNext(ConsumableString text) {
        TokenDef token = null;
        Matcher matcher = pattern.matcher(text.get());
        if (matcher.find()) {
            token = new TokenDef(tokenName, text.consume(matcher.group(groupNo)), this);
        }
        return token;
    }
}
