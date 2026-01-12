package de.addiks.einsicht.abstract_syntax_tree;

import org.jspecify.annotations.Nullable;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.function.BiConsumer;
import java.util.function.BiFunction;
import java.util.function.Function;

public class ASTIterator implements Iterator<ASTNode>, Iterable<ASTNode> {
    private final ASTNode root;
    private ASTNode next;

    private List<StackEntry> stack = new ArrayList();

    public ASTIterator(ASTNode root) {
        this.root = root;
        next = root;
    }

    @Override
    public boolean hasNext() {
        return next != null;
    }

    @Override
    public ASTNode next() {
        try {
            return next;
        } finally {
            increment();
        }
    }

    public void skipNode() {
        if (next == null) {
            return;
        }
        if (stack.isEmpty()) {
            next = null;
            return;
        }
        ASTBranch parent = next.parent();
        StackEntry stackEntry = stack.getLast();
        if (stackEntry.position == 0) {
            stack.removeLast();
            increment();
        }
    }

    private void increment() {
        if (next == null) {
            return;
        }
        if (!next.prepended().isEmpty()) {
            next = next.prepended().getFirst();
            stack.add(new StackEntry(StackChildType.PREPENDED, 0));

        } else if (!next.children().isEmpty()) {
            next = next.children().getFirst();
            stack.add(new StackEntry(StackChildType.CHILDREN, 0));

        } else if (!next.appended().isEmpty()) {
            next = next.appended().getFirst();
            stack.add(new StackEntry(StackChildType.APPENDED, 0));

        } else if (!stack.isEmpty()) {
            ASTBranch parent = next.parent();
            while (true) {
                if (stack.isEmpty()) {
                    next = null;
                    break;
                }
                StackEntry stackEntry = stack.getLast();
                List<ASTNode> children = stackEntry.type.of(parent);
                if (children.size() <= stackEntry.position + 1) {
                    stackEntry.type = stackEntry.type.next();
                    stackEntry.position = -1;
                    if (stackEntry.type == null) {
                        stack.removeLast();
                    }
                } else {
                    if (stackEntry.position < children.size() - 2) {
                        stackEntry.position++;
                        next = children.get(stackEntry.position);
                        break;
                    }
                }
            }
        } else {
            next = null;
        }
    }

    public static <R> R deepMap(
            ASTRoot root,
            Function<ASTNode,R> onNode,
            BiFunction<R,List<R>, R> onParentCompleted
    ) {
        ASTIterator iterator = new ASTIterator(root);
        int stackSizeBefore = iterator.stack.size();
        List<R> parentStack = new ArrayList<>();
        List<List<R>> resultStack = new ArrayList<>();
        R result = null;

        parentStack.add(onNode.apply(root));
        resultStack.add(new ArrayList<>());

        while (iterator.hasNext()) {
            ASTNode node = iterator.next();
            R nodeResult = onNode.apply(node);

            if (node == root) {
                result = nodeResult;
            }

            if (iterator.stack.size() < stackSizeBefore) {
                R oldParent = parentStack.removeLast();
                R newParent = onParentCompleted.apply(oldParent, resultStack.removeLast());
                resultStack.getLast().set(resultStack.getLast().indexOf(oldParent), newParent);
                if (result == oldParent) {
                    result = newParent;
                }

            } else {
                resultStack.getLast().add(nodeResult);
                if (iterator.stack.size() > stackSizeBefore) {
                    parentStack.add(nodeResult);
                    resultStack.add(new ArrayList<>());
                }
            }
        }
        return result;
    }

    @Override
    public Iterator<ASTNode> iterator() {
        return this;
    }

    private static class StackEntry{
        public StackChildType type;
        public int position;
        public StackEntry(StackChildType type, int position) {
            this.type = type;
            this.position = position;
        }
    }
    private enum StackChildType {
        PREPENDED, CHILDREN, APPENDED;
        public StackChildType next() {
            if (this == PREPENDED) {
                return CHILDREN;
            } else if (this == CHILDREN) {
                return APPENDED;
            }
            return null;
        }
        public List<ASTNode> of(ASTNode node) {
            if (this == PREPENDED) {
                return node.prepended();
            } else if (this == CHILDREN) {
                return node.children();
            } else {
                return node.appended();
            }
        }
    }
}
