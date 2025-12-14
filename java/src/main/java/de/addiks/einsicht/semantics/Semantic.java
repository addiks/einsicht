package de.addiks.einsicht.semantics;

import de.addiks.einsicht.abstract_syntax_tree.ASTBranch;

import java.util.List;

public interface Semantic {
    String name();

    interface Local extends Semantic {
        ASTBranch node();
    }

    interface Contextual extends Semantic {
        List<Semantic> related();
    }

    interface Factory {
        interface Local extends Factory {
            Semantic.Local forBranch(ASTBranch branch);
        }

        interface Contextual extends Factory {
            Semantic.Contextual combine(Semantic root, List<Semantic> related);
            Class<? extends Semantic> root();
            boolean isRelatedTo(Semantic root, Semantic possibleCandidate);
            List<Class<? extends Semantic>> related();
        }
    }
}
