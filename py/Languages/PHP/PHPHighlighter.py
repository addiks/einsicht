
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont
from PySide6.QtCore import QRegularExpression, Qt

class PHPHighlighter(QSyntaxHighlighter):
    
    def highlightBlock(self, text):

        defFormat = QTextCharFormat()
        defFormat.setFontWeight(QFont.Bold)
        defFormat.setForeground(Qt.darkMagenta)

        expression = QRegularExpression("def")

        scanner = expression.globalMatch(text)

        while scanner.hasNext():
            match = scanner.next()
            print(match)
            self.setFormat(match.capturedStart(), match.capturedLength(), defFormat)
