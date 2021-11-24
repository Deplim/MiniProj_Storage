import sys
from enum import Enum

# DKU - JeongEuiRyeong - 2021.11.24


class MiniCScanner:
    """MiniCScanner

    getToken() : 실행될 때마다 토큰 하나씩 추출
    exceptComment() : source 코드에서 주석문 모두 삭제
    """

    OPERATION_CHARS = "+-*/%=!&|!<>"  # 연산자 문자
    SINGLE_ST = "[]{}(),;‘’"  # 기호 문자
    HEX_ALPHA = "ABCDEF"  # 16진수에서 알파벳으로 들어가는 문자
    # 연산자 리스트
    OPERATOR = ["+", "-", "*", "/", "%", "=", "!", "&&", "||", "==", "!=", "<", ">", "<=", ">="]
    # State Diagram (상태 전이도) 에서 final state 가 될 수 있는 state
    FINAL_STATE = ["IDorKeyword", "Zero", "Hex", "Oct", "Dec", "Operator", "SingleOperator", "ConstD_", "ConstS_",
                   "RealN_", "RealNe_"]
    flag = None  # getToken 을 다시 실행할때 이전의 state 를 그대로 받아오고 싶은 경우 사용

    """ graph

    state diagram 을 Dictionary 로 구현. 
    key = state name, value(dict) : Input and target state

    state list ->
        Initial, IDorKeyword, Zero, PreHex, Hex, Oct, Dec, Operator, SingleOperator
        Const, ConstS, ConstD, ConstS_, ConstD_
        RealN, RealN_, RealNe, RealNe2, RealNe_ 
    """
    graph = {"Initial": {"whitespace": "Initial", "OC": "Operator", "SSC": "SingleOperator", "Alphabet": "IDorKeyword",
                         "_": "IDorKeyword", "0": "Zero", "digit except 0": "Dec", "‘": "Const"},
             "IDorKeyword": {"digit": "IDorKeyword", "Alphabet": "IDorKeyword"},
             "Dec": {"digit": "Dec", ".": "RealN", "e": "RealNe"},
             "Zero": {"digit": "Oct", "x": "PreHex", ".": "RealN"},
             "Oct": {"digit": "Oct"},
             "PreHex": {"digit": "Hex", "HEX_ALPHA": "Hex"},
             "Hex": {"digit": "Hex", "HEX_ALPHA": "Hex"},
             "Operator": {"OC": "Operator"},
             "SingleOperator": {},
             "Const": {"Alphabet": "ConstS", "digit": "ConstD"},
             "ConstS": {"Alphabet": "ConstS", "’": "ConstS_"},
             "ConstS_": {},
             "ConstD": {"digit": "ConstD", "’": "ConstS_"},
             "ConstD_": {},
             "RealN": {"digit": "RealN_"},
             "RealN_": {"digit": "RealN_", "e": "RealNe"},
             "RealNe": {"+": "RealNe2", "-": "RealNe2"},
             "RealNe2": {"digit": "RealNe_"},
             "RealNe_": {"digit": "RealNe_"}
    }

    def __init__(self, filePath, printSrc=False):
        self.__idx = 0
        self.SYMBOL_TABLE = SymbolTable() # scanner 인스턴스를 생성할 때 symbol_table 도 생성

        # 소스코드가 있는 파일을 가져오고, 정상적으로 로드하지 못한 경우 오류 발생 
        try:
            with open(filePath, 'r', encoding='UTF-8') as f:
                self.__src = f.read()
        except Exception:
            raise Exception(LexicalError.CannotOpenFile.value)

        # exceptComment 를 실행시켜서 주석문을 제거하는 과정에 오류가 없는지 확인
        if self.exceptComment():
            raise Exception(LexicalError.InvalidComment.value)

        # getToken 은 현제 state 에서 받을 수 없는 Input 이 들어와야 token 을 출력하도록 되어있으므로 
        # 마지막 token 을 받기 위해서 " " 을 src 에 추가.
        self.__src += " "

        # printSrc = True 로 받은 경우, 주석문 제거된 source code 출력
        if printSrc:
            print("========================")
            print(self.__src)
            print("========================\n")

    def getToken(self):
        token = Token(self.SYMBOL_TABLE)
        tokenString = ""

        state = "Initial"
        # flag 가 있는 경우 저장된 state (이전 getToken 실행에서 멈춘 state) 를 가져옴. 
        if self.flag:
            state = self.flag
            self.flag = None # 다시 None 으로 비움.

        # Initial state 에서 시작해 graph 에서 더 갈수 있는 곳이 없거나 src 를 다 읽을 때까지 반복.
        while self.__idx != len(self.__src):
            c = self.__src[self.__idx] # src 에서 문자 하나 읽기
            self.__idx += 1

            # Input 값의 종류 확인하기
            Input = ""
            if c.isspace():
                Input = "whitespace"
            if c.isalpha():
                Input = "Alphabet"
            if c.isdigit():
                Input = "digit"
            if c in self.OPERATION_CHARS:
                Input = "OC"
            if c in self.SINGLE_ST:
                Input = "SSC"
            if c == "_" or c == "." or c == "‘" or c == "’":
                Input = c

            # state 에 따라 Input 값을 따로 인식해야 하는 경우
            if state == "Initial":
                if c.isdigit():
                    Input = "digit except 0"
                if c == "0":
                    Input = c
            if state == "Zero":
                if c == "x":
                    Input = c
            if state == "Hex" or "PreHex":
                if c in self.HEX_ALPHA:
                    Input = "HEX_ALPHA" 
            if state == "RealN_":
                if c == "e":
                    Input = c
            if state == "RealNe":
                if c == "+" or c == "-":
                    Input = c

            # 그래프를 확인하고 state 이동
            if Input in self.graph[state]:
                state = self.graph[state][Input]
                if Input != "whitespace": # 문자가 공백이 아니라면 string 에 추가
                    tokenString += c

                """
                따옴표 (‘, ’) 는 그 자체로 토큰이면서, 동시에 상수를 구별하기 위한 요소이므로
                상수와 관련된 state 를 거치는 경우, 따옴표도 token 으로 출력될 수 있도록 추가 코드 작성함. 
                """
                # 왼쪽 따옴표 "‘" 를 만난경우 token 으로 출력하고 state 는 유지
                if state == "Const": 
                    self.flag = state
                    break

                # 오른쪽 따옴표 "’" 를 만난경우 
                elif state == "ConstD_":
                    # tokenString 에 "’" 이외의 문자가 있는경우
                    if len(tokenString)>1:
                        tokenString = tokenString[:-1]
                        self.__idx -= 1
                        self.flag = "ConstD" # idx 와 state 한단계 이전으로 돌림.
                    # tokenString 에 "’" 만 있는 경우에는 "’" 를 token 으로 출력
                elif state == "ConstS_":
                    if len(tokenString)>1:
                        tokenString = tokenString[:-1]
                        self.__idx -= 1
                        self.flag = "ConstS"
            
            # graph 에서 갈 수 있는 state 가 없는 경우
            else:
                # 현제 state 가 final state 가 아니라면, 인식할 수 없는 token 이 있는 것이므로 오류 발생
                if state not in self.FINAL_STATE: 
                    raise Exception(LexicalError.InvalidSymbol.value)
                
                # final state 상태라면 idx 에서 1을 뺀 후 (다시 getToken() 을 실행할 때 현재 문자부터 인식하기 위해) token 출력
                else :
                    self.__idx -= 1
                    break
        
        # 연산자를 인식한 경우 OPERATOR list 에 있는지 확인
        # graph 의 Operator state 에서 연산자 문자를 받는데 제약이 없기 때문에 이 단계에서 확인해야 함.
        if state == "Operator" and tokenString not in self.OPERATOR:
            raise Exception(LexicalError.InvalidOperator.value)

        # 인식한 token string 이 있는 경우
        if tokenString != "":
            # token 인스턴스에서 state 와 string 를 받아 출력할 token symbol 과 value 를 구하도록 함.
            token.setSymbol(state, tokenString) 
            return token.get_token()
        # 인식한 token string 이 없으면 false 반환
        else:
            return False

    # comment 삭제 과정에서 오류가 있는 경우 True, 없는 경우 False 반환
    def exceptComment(self):
        target =  self.__src
        while 1:
            left_c = target.find("(*")
            right_c = target.find("*)")  # 좌측, 우측 comment 기호를 각각 탐색
            
            # 두 기호가 다 없으면 주석문이 없는 것이므로 break
            if left_c == -1 and right_c == -1: 
                break

            # 두 기호가 다 있는 경우 주석문 부분 삭제 
            if left_c != -1 and right_c != -1:
                if left_c > right_c: # 두 기호가 다 있지만 순서가 잘못된 경우 오류 발생
                    return True
                target = target[:left_c]+target[right_c+2:]
            else:  # 한쪽 기호만 있는경우 주석문을 잘못 작성한 것이므로 오류 발생
                return True

        self.__src = target  # 주석문이 삭제된 소스코드 저장
        return False


class LexicalError(Enum):
    """LexicalError

    발생할 수 있는 Lexical Error 종류를 속성으로 가지고 있음.
    """

    CannotOpenFile = "Lexical Error - 소스 파일을 불러오지 못함."
    InvalidComment = "Lexical Error - 주석문이 올바르게 작성되지 않음."
    InvalidSymbol = "Lexical Error - 인식할 수 없는 token."
    InvalidOperator = "Lexical Error - 잘못된 연산자."


class Token:
    """Token

    setSymbol() : 현재 state 와 token string 을 받아 출력할 token symbol 과 val 을 구함.
    get_token() : token symbol 과 val 을 string 형식으로 반환.
    """

    TokenSymbol = {  # 토큰 번호를 추출하기 위한 딕셔너리
        "tident": 3, "tconst": 4,
        "Dec": 5, "Oct": 6, "Hex": 7, "treal": 8,

        "+": 10, "-": 11, "*": 12, "/": 13, "%": 14, "=": 15, "!": 16, "&&": 17,
        "||": 18, "==": 19, "!=": 20, "<": 21, ">": 22, "<=": 23, ">=": 24,

        "[": 30, "]": 31, "{": 32, "}": 33, "(": 34, ")": 35, ",": 36, ";": 37, "‘": 38, "’": 39,

        "if": 40, "while": 41, "for": 42, "const": 43, "int": 44, "float": 45, "else": 46,
        "return": 47, "void": 48, "break": 49, "continue": 50, "char": 51
    }
    OP_TABLE = ["if", "while", "for", "const", "int", "float", "else", "return", "void", "break", "continue", "char"]

    def __init__(self, symbolTable):
        self.__symbol = None # token symbol (토큰 번호)
        self.__val = "0" # token value
        self.__tokenString = ""
        self.__symbolTable = symbolTable 

    def setSymbol(self, state, tokenS):
        self.__tokenString = tokenS

        # state 가 IDorKeyword (문자열 token) 인 경우 예약어 테이블을 확인하고, 그곳에 있으면 예약어 토큰으로, 없으면 사용자 정의어(tident)로 간주.
        if state == "IDorKeyword":
            if tokenS in self.OP_TABLE:
                self.__symbol = self.TokenSymbol[tokenS]
            else:
                tident_num = self.__symbolTable.check_symbol(tokenS)
                self.__symbol = self.TokenSymbol["tident"]
                self.__val = tident_num

        # 정수, 실수, 상수에 대해서는 value 에 token string 을 넣음.
        elif state in ("Zero", "Dec", "Oct", "Hex"):
            if state == "Zero":
                self.__symbol = self.TokenSymbol["Dec"]
            else:
                self.__symbol = self.TokenSymbol[state]
            self.__val = tokenS
        
        elif state in ("RealN_", "RealNe_"):
            self.__symbol = self.TokenSymbol["treal"]
            self.__val = tokenS
        
        elif state == "Const":  # 왼쪽 따옴표
            self.__symbol = self.TokenSymbol["‘"]
        elif state in ("ConstD_", "ConstS_"):
            if '’' not in tokenS:
                self.__symbol = self.TokenSymbol["tconst"] # 
                self.__val = tokenS
            else:
                self.__symbol = self.TokenSymbol["’"]  # 오른쪽 따옴표
        
        # 연산자와 기호의 경우 따로 value 를 설정하지 않고 (default = "0"), token symbol 에 token string 을 넣음.
        elif state == "Operator":
            self.__symbol = self.TokenSymbol[tokenS]

        elif state == "SingleOperator":
            self.__symbol = self.TokenSymbol[tokenS]

    def get_token(self):
        return "{0: <10} : ({1}, {2})".format(self.__tokenString, self.__symbol, self.__val)


class SymbolTable:
    """SymbolTable

    check_symbol() : token 이 사용자 정의어인 경우 symbol table 에 해당 문자열이 있으면 번호 반환, 없으면 새로 설정하고 번호 반환.
    getSymbolTable() : symbol table (dictionary) 반환
    """
    def __init__(self):
        self.__Table = {}
        self.__count = 1  # 사용자 정의어의 번호를 지정하기 위해 사용하는 변수.

    def check_symbol(self, s):
        if s in self.__Table:
            return self.__Table[s]
        else :
            self.__Table[s] = self.__count
            self.__count += 1 
            return self.__Table[s]

    def getSymbolTable(self):
        return self.__Table


if __name__ == "__main__":
    if len(sys.argv) <=1:
        raise Exception("\nPlease enter the file path (by argument)")
    sc = MiniCScanner(sys.argv[1]) # MiniCScanner 인스턴스 생성

    # 토큰 스트림 출력
    print("\n token stream ----")
    while 1:
        tok = sc.getToken()
        if tok is False:
            break
        else:
            print(tok)
    
    # 심볼 테이블 출력
    print("\n symbol table ----")
    print(sc.SYMBOL_TABLE.getSymbolTable())
