
from .Language import Language

from collections import OrderedDict

class PHPLanguage(Language):
    
    def syntaxHighlighter(self, document):
        return PythonHighlighter(document)


    def tokens(self): # OrderedDict
        tokens = OrderedDict()
        tokens['T_AND_EQUAL']                = "&=" #
        tokens['T_ARRAY_CAST']               = "\\(array\\)" #
        #tokens['T_BAD_CHARACTER']            = "" ASCII < 32 TODO!
        tokens['T_BOOLEAN_AND']              = "&&" #
        tokens['T_BOOLEAN_OR']               = "\\|\\|" #
        tokens['T_BOOL_CAST']                = "\\(bool(ean)?\\)" #
        #tokens['T_CHARACTER']                = "" ???
        tokens['T_CLASS_C']                  = "__CLASS__" #
        tokens['T_CLOSE_TAG']                = "(\\?|\\%)\\>" #
        tokens['T_DOC_COMMENT']              = "\\/\\*\\*.*?\\*\\/" #
        tokens['T_COMMENT']                  = "(//[^\n]*?(?=\n|\\?\\>|\\%\\>)|\\#[^\n]*?(?=\n|\\?\\>|\\%\\>))|/\\*.*?\\*/" #
        tokens['T_CONCAT_EQUAL']             = "\\.=" #
        # tokens['T_CONSTANT_ENCAPSED_STRING'] = "\"(?:[^\"\\\\]|\\\\.)*\"|\'(?:[^\'\\\\]|\\\\.)*\'" #
        # tokens['T_EXECUTE_STRING']           = "\`(?:[^\`\\\\]|\\\\.)*\`"
        #tokens['T_CURLY_OPEN']               = "\\{\\$"
        tokens['T_DEC']                      = "--" #
        tokens['T_DIR']                      = "__DIR__" #
        tokens['T_DIV_EQUAL']                = "/=" #
        tokens['T_DNUMBER']                  = "\\d+\\.\\d+" #
        #tokens['T_DOLLAR_OPEN_CURLY_BRACES'] = "\\$\\{"
        tokens['T_DOUBLE_ARROW']             = "=>" #
        tokens['T_DOUBLE_CAST']              = "\\((real|double|float)\\)" #
        tokens['T_DOUBLE_COLON']             = "::" #
        #tokens['T_ENCAPSED_AND_WHITESPACE']  = "\\'.*?\\'" ???
        tokens['T_EXIT']                     = "(exit|die)" #
        tokens['T_FILE']                     = "__FILE__" #
        tokens['T_FUNCTION']                 = "c?function(?!\\w)" #
        tokens['T_FUNC_C']                   = "__FUNCTION__" #
        tokens['T_HALT_COMPILER']            = "__halt_compiler(\\w+)" #
        # tokens['T_HEREDOC']                  = "<<<\s*[\'\"]?(.*)[\'\"]?\\n.*?\\n\\1;?" #
        tokens['T_INC']                      = "\\+\\+" #
        tokens['T_INLINE_HTML']              = "\\0WILL#NEVER~PARSE" #
        tokens['T_INT_CAST']                 = "\\(int(eger)?\\)" #
        tokens['T_ISSET']                    = "isset(?!\\w)" #
        tokens['T_IS_IDENTICAL']             = "===" #
        tokens['T_IS_EQUAL']                 = "==" #
        tokens['T_IS_GREATER_OR_EQUAL']      = ">=" #
        tokens['T_IS_NOT_IDENTICAL']         = "!==" #
        tokens['T_IS_NOT_EQUAL']             = "(\\!=|<>)" #
        tokens['T_IS_SMALLER_OR_EQUAL']      = "<=" #
        tokens['T_LINE']                     = "__LINE__" #
        # tokens['T_LNUMBER']                  = "(\d+|0x[0-9a-f]+)"
        tokens['T_METHOD_C']                 = "__METHOD__" #
        tokens['T_MINUS_EQUAL']              = "-=" #
        tokens['T_MOD_EQUAL']                = "\\%=" #
        tokens['T_MUL_EQUAL']                = "\\*=" #
        tokens['T_NS_C']                     = "__NAMESPACE__" #
        tokens['T_NS_SEPERATOR']             = "\\\\" #
        #tokens['T_NUM_STRING']               = "" ???
        tokens['T_OBJECT_CAST']              = "\\(object\\)" #
        tokens['T_OBJECT_OPERATOR']          = "->" #
        #tokens['T_OLD_FUNCTION']             = "" ???
        tokens['T_OPEN_TAG']                 = "<(\\?php|\\%|\\?|\\?=)" #
        tokens['T_OR_EQUAL']                 = "\\|=" #
        tokens['T_PAAMAYIM_NEKUDOTAYIM']     = "::" #
        tokens['T_PHP_START']                = "\0WILL#NEVER~PARSE" #
        tokens['T_PLUS_EQUAL']               = "\\+=" #
        tokens['T_SL']                       = "<<" #
        tokens['T_SL_EQUAL']                 = "<<=" #
        tokens['T_SR']                       = ">>" #
        tokens['T_SR_EQUAL']                 = ">>=" #
        tokens['T_STRING_CAST']              = "\\(string\\)" #
        #tokens['T_STRING_VARNAME']           = "" ??? (something to do with '${somevar}')
        tokens['T_SINGLE_CHAR']              = "\0WILL#NEVER~PARSE" #
        tokens['T_UNSET_CAST']               = "\\(unset\\)" #
        tokens['T_VARIABLE']                 = "\\$+[a-zA-Z_][a-zA-Z0-9_]*" #
        tokens['T_WHITESPACE']               = "\\s+" #
        tokens['T_XOR_EQUAL']                = "\\^=" #
        #tokens['T_STRING']                   = "[a-zA-Z_\\\\][a-zA-Z0-9_\\\\]*"
        tokens['T_STRING']                   = "[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff\\\\]*" #

        return tokens

    def directTokenMap(self): # dict
        return {
            '(unset)':         self.tokenNumber('T_UNSET_CAST'),
            '(bool)':          self.tokenNumber('T_BOOL_CAST'),
            '(boolean)':       self.tokenNumber('T_BOOL_CAST'),
            '(array)':         self.tokenNumber('T_ARRAY_CAST'),
            '(real)':          self.tokenNumber('T_DOUBLE_CAST'),
            '(double)':        self.tokenNumber('T_DOUBLE_CAST'),
            '(float)':         self.tokenNumber('T_DOUBLE_CAST'),
            '(object)':        self.tokenNumber('T_OBJECT_CAST'),
            '(int)':           self.tokenNumber('T_INT_CAST'),
            '(integer)':       self.tokenNumber('T_INT_CAST'),
            '(string)':        self.tokenNumber('T_STRING_CAST'),
            'exit':            self.tokenNumber('T_EXIT'),
            'die':             self.tokenNumber('T_EXIT'),
            '__FILE__':        self.tokenNumber('T_FILE'),
            '__FUNCTION__':    self.tokenNumber('T_FUNC_C'),
            '__halt_compiler': self.tokenNumber('T_HALT_COMPILER'),
            '__LINE__':        self.tokenNumber('T_LINE'),
            '__METHOD__':      self.tokenNumber('T_METHOD_C'),
            '__NAMESPACE__':   self.tokenNumber('T_NS_C'),
            '__CLASS__':       self.tokenNumber('T_CLASS_C'),
            '__DIR__':         self.tokenNumber('T_DIR'),
            '\\':              self.tokenNumber('T_NS_SEPERATOR'),
        }

    def keywords(self): # list
        return [
            'abstract', 'array', 'as', 'break', 'case',
            'catch', 'class', 'clone', 'const', 'continue',
            'declare', 'default', 'do', 'echo', 'else',
            'elseif', 'empty', 'enddeclare', 'endfor',
            'endforeach', 'endif', 'endswitch', 'endwhile',
            'eval', 'extends', 'final', 'for', 'foreach', 'function',
            'global', 'goto', 'if', 'implements', 'include',
            'include_once', 'instanceof', 'interface', 'isset',
            'isset', 'list', 'and', 'or', 'xor', 'new',
            'print', 'private', 'public', 'protected',
            'require', 'require_once', 'return', 'static',
            'switch', 'throw', 'try', 'unset', 'use', 'var',
            'while'
        ]

    def specialChars(self): # list
        return [
            '<', '>', '+', '-', '*', '/', '%',
            '(', ')', '[', ']', '{', '}',
            ',', '.', ';', ':', '?',
            '^', '~', '&', '|', '#',
            '=', '!', '@', '$'
        ]

    def operators(self): # dict
        return {
            "&=":  self.tokenNumber('T_AND_EQUAL'),
            "&&":  self.tokenNumber('T_BOOLEAN_AND'),
            "||":  self.tokenNumber('T_BOOLEAN_OR'),
            "/=":  self.tokenNumber('T_DIV_EQUAL'),
            "=>":  self.tokenNumber('T_DOUBLE_ARROW'),
            "==":  self.tokenNumber('T_IS_EQUAL'),
            ">=":  self.tokenNumber('T_IS_GREATER_OR_EQUAL'),
            "!=":  self.tokenNumber('T_IS_NOT_EQUAL'),
            "<>":  self.tokenNumber('T_IS_NOT_EQUAL'),
            "<=":  self.tokenNumber('T_IS_SMALLER_OR_EQUAL'),
            "-=":  self.tokenNumber('T_MINUS_EQUAL'),
            "%=":  self.tokenNumber('T_MOD_EQUAL'),
            "*=":  self.tokenNumber('T_MUL_EQUAL'),
            "<<":  self.tokenNumber('T_SL'),
            ">>":  self.tokenNumber('T_SR'),
            "::":  self.tokenNumber('T_PAAMAYIM_NEKUDOTAYIM'),
            "->":  self.tokenNumber('T_OBJECT_OPERATOR'),
            "^=":  self.tokenNumber('T_XOR_EQUAL'),
            "++":  self.tokenNumber('T_INC'),
            "--":  self.tokenNumber('T_DEC'),
            ".=":  self.tokenNumber('T_CONCAT_EQUAL'),
        }
