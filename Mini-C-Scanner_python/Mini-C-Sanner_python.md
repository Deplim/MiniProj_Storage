# Mini-C-Scanner_python
<br><br>
2021//11/24  
DKU – 오토마타와 컴파일러 : 스캐너 만들기  

## 기능에 대한 설명
**Mini C (C 언어의 일부 어휘를 가져온 가상의 언어) 를 대상으로 하는 스캐너 프로그램**  
**형식언어 – DFA Automata 를 기반으로 함.**  
> **스캐너(scanner) OR 어휘 분석기(lexical analyzer) 란** : 컴파일러의 일부로, 구문 분석기에서 호출하는 모듈.  
> 소스 프로그램을 읽어 토큰(token) 이라는 문법적으로 의미 있는 최소의 단위로 분리하는 것으로 토큰 스트림(stream) 을 출력함.  

**이때 토큰은 토큰번호(token number)와 토큰 값(token value)의 순서쌍으로 표현**  
**-> (토큰 번호, 토큰 값)**  
<br><br>

스캐너 프로그램은 총 4가지 클래스로 구성함.
1.	MiniCScanner : 토큰 생성을 담당하는 클래스. 생성시 소스파일 경로를 입력 받으며, getToken 메소드를 실행할 때마다 토큰을 하나씩 반환함.
2.	LexicalError : Lexical Error 의 종류와 출력할 문자열이 들어있는 클래스.
3.	Token : MiniCScanner 에서 getToken 을 실행할 때마다 생성하는 token 객체 클래스. 
4.	SymbolTable : 사용자 정의어의 목록과 번호를 저장하는 테이블 클래스
<br>

## 각 토큰에 대한 설명 및 DFA
1. **주석문(Comment)**  
  Block Comment (* ... *)
2. **사용자 정의어(Id)**  
  첫글자는 _ 또는 영문자, 나머지는 영문자 숫자의 조합, no blank
  예약어(Reserved Word)는 제외
3. **상수**  
  예) 숫자 상수 “10”, 문자 상수 “abc”
4. **정수**  
  10진수(Decimal Number) : 0으로 시작하지 않는 일반 숫자. (eg. 526)  
  8진수(Octal Number) : 0으로 시작하는 숫자. (eg. 0526)  
  16진수(Hexa-decimal Number) : 0x로 시작하는 숫자 혹은 알파벳 AF.(1F) (eg. 0xFF, 0xff)  
5. **실수**  
  10.5, 13e+2, 20.3e-5
6. **예약어(Reserved words)**  
  const, else, if, int, char, float return, void, while, for, break, continue
7. **연산자(Operator)**  
  사칙 연산자 : +, -, *, /, %  
  배정 연산자 : =  
  논리 연산자 : !, &&, ||  
  관계 연산자 : ==, !=, <, >, <=, >=  
8. **기호**  
  대괄호('[', ']'), 중괄호('{', '}'), 소괄호('(', ')'), 컴마(','), 세미콜론(';').  
  따옴표 (‘“’, ‘”,)
<br>

### 토큰의 종류 및 번호
| 토큰 종류 | 토큰 번호 | 참고 |
| ---- | ---- | ---- |
| 식별자(tident) - 사용자 정의어 | 3 | |
| 상수(tconst) | 4 | 문자열(리터럴) |
| 정수(tint) | 5~7 | 5(10진수), 6(8진수), 7(16진수) |
| 실수(treal) | 8 | |
| 연산자 | 10 ~ 24 | +, -, ... |
| 특수 기호 | 30 ~ 39 | [ , ] , { , ... |
| 예약어 | 40 ~ | if, while, ... |
<br>

### DFA - State diagram (상태 전이도)
(관련 [오픈소스](https://github.com/MinJunKweon/Mini-C-Scanner/blob/master/report/%ED%98%95%EC%8B%9D%EC%96%B8%EC%96%B4-Mini%20C%20Scanner%20%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8.md) 참고함)  

![mcsp_i1](https://github.com/Deplim/MiniProj_Storage/blob/main/Mini-C-Scanner_python/img/mcsp_i1.png?raw=true)  

위의 state diagram 에서 **상수** 와 **실수** 를 구현하기 위해 아래와 같은 state를 추가로 구현하였음.  

![mcsp_i2](https://github.com/Deplim/MiniProj_Storage/blob/main/Mini-C-Scanner_python/img/mcsp_i2.png?raw=true)
<br>

## 프로그램 설계

먼저 DFA 를 만들고 나면, 그것을 그대로 graph 로 구현하기로 계획함.  <br>

참고했던 코드에서는 state 를 인식하는 과정을 if else 문을 이용하여 구현했는데, 문자의 종류를 판단하고 현재의 state 와 비교하여 그 다음 state 로 이동하는 로직을 만들어야 한다는 점에서 어떻게 구현하든 근본적인 부분은 동일하다고 생각하였음.  <br>

그래프는 Dictionary 를 이용하여 구현하였고, 각 state 와 Input 는 String으로 표현함.  <br>

또한 여러 개의 token 을 인식하는 프로그램이었기 때문에, graph 탐색 과정에 현재 state 에서 받을 수 없는 Input 이 들어오는 경우 이전까지 탐색한 문자열과 state 를 이용하여 token 을 생성한 다음 Initial state 에서 다시 시작하도록 설계하였음.  <br>

마지막으로 Symbol table 에서는 식별자 탐색에 O(1) 의 시간이 걸리도록 하기 위해 Dictionary (hash table) 을 사용함.  <br>
<br>

## 프로그램 소스 코드
```python
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
            elif c.isalpha():
                Input = "Alphabet"
            elif c.isdigit():
                Input = "digit"
            elif c in self.OPERATION_CHARS:
                Input = "OC"
            elif c in self.SINGLE_ST:
                Input = "SSC"
            
            if c == "_" or c == "." or c == "‘" or c == "’":
                Input = c

            # state 에 따라 Input 값을 따로 인식해야 하는 경우
            if state == "Initial":
                if c.isdigit():
                    Input = "digit except 0"
                if c == "0":
                    Input = c
            elif state == "Zero":
                if c == "x":
                    Input = c
            elif (state == "Hex") or (state == "PreHex"):
                if c in self.HEX_ALPHA:
                    Input = "HEX_ALPHA" 
            elif (state == "Dec") or (state == "RealN_"): 
                if c == "e":
                    Input = c
            elif state == "RealNe":
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
    
```
<br>

## 입력 소스 코드

**@ sample program #1 (no error)**
```
int a, b, sum;
float x1, y1, zoom;
char ch1;
if (a>b) then sum = a+b
else sum = a+10;
while (a ==b) {
  zoom = (sum + x1)/10;
  ch1 = ‘123’;
}
```

**@ sample program #2 (error** **포함)**
```
int a1, 2b;
float x2, y2;
a1 := 100;
x2 = 12.23e+10;
```


**@ sample program #3 (custom)**
```
(* DKU JeongEuiRyeong *)
int a = 0xF3, b = 1;
float _asdf = 13.29e+12;
b = a % b;

(* comment example *)

if ((a>b) && (_asdf>=b)) {
    a = a*b;
}
else {
    a = a/b;
}
```
<br>

## 실행 결과 : 토큰 목록 및 심볼 테이블
**@ sample program #1 (no error)**
```
 
 token stream ----
int        : (44, 0)
a          : (3, 1)
,          : (36, 0)
b          : (3, 2)
,          : (36, 0)
sum        : (3, 3)
;          : (37, 0)
float      : (45, 0)
x1         : (3, 4)
,          : (36, 0)
y1         : (3, 5)
,          : (36, 0)
zoom       : (3, 6)
;          : (37, 0)
char       : (51, 0)
ch1        : (3, 7)
;          : (37, 0)
if         : (40, 0)
(          : (34, 0)
a          : (3, 1)
>          : (22, 0)
b          : (3, 2)
)          : (35, 0)
then       : (3, 8)
sum        : (3, 3)
=          : (15, 0)
a          : (3, 1)
+          : (10, 0)
b          : (3, 2)
else       : (46, 0)
sum        : (3, 3)
=          : (15, 0)
a          : (3, 1)
+          : (10, 0)
10         : (5, 10)
;          : (37, 0)
while      : (41, 0)
(          : (34, 0)
a          : (3, 1)
==         : (19, 0)
b          : (3, 2)
)          : (35, 0)
{          : (32, 0)
zoom       : (3, 6)
=          : (15, 0)
(          : (34, 0)
sum        : (3, 3)
+          : (10, 0)
x1         : (3, 4)
)          : (35, 0)
/          : (13, 0)
10         : (5, 10)
;          : (37, 0)
ch1        : (3, 7)
=          : (15, 0)
‘          : (38, 0)
123        : (4, 123)
’          : (39, 0)
;          : (37, 0)
}          : (33, 0)

 symbol table ----
{'a': 1, 'b': 2, 'sum': 3, 'x1': 4, 'y1': 5, 'zoom': 6, 'ch1': 7, 'then': 8}

```

**@ sample program #2 (error** **포함)**
```
 
 token stream ----
int        : (44, 0)
a1         : (3, 1)
,          : (36, 0)
2          : (5, 2)
b          : (3, 2)
;          : (37, 0)
float      : (45, 0)
x2         : (3, 3)
,          : (36, 0)
y2         : (3, 4)
;          : (37, 0)
a1         : (3, 1)
Traceback (most recent call last):
  File "scanner.py", line 321, in <module>
    tok = sc.getToken()
  File "scanner.py", line 164, in getToken
    raise Exception(LexicalError.InvalidSymbol.value)
Exception: Lexical Error - 인식할 수 없는 token.

```
**@ sample program #3 (custom)**
```

 token stream ----
int        : (44, 0)
a          : (3, 1)
=          : (15, 0)
0xF3       : (7, 0xF3)
,          : (36, 0)
b          : (3, 2)
=          : (15, 0)
1          : (5, 1)
;          : (37, 0)
float      : (45, 0)
_asdf      : (3, 3)
=          : (15, 0)
13.29e+12  : (8, 13.29e+12)
;          : (37, 0)
b          : (3, 2)
=          : (15, 0)
a          : (3, 1)
%          : (14, 0)
b          : (3, 2)
;          : (37, 0)
if         : (40, 0)
(          : (34, 0)
(          : (34, 0)
a          : (3, 1)
>          : (22, 0)
b          : (3, 2)
)          : (35, 0)
&&         : (17, 0)
(          : (34, 0)
_asdf      : (3, 3)
>=         : (24, 0)
b          : (3, 2)
)          : (35, 0)
)          : (35, 0)
{          : (32, 0)
a          : (3, 1)
=          : (15, 0)
a          : (3, 1)
*          : (12, 0)
b          : (3, 2)
;          : (37, 0)
}          : (33, 0)
else       : (46, 0)
{          : (32, 0)
a          : (3, 1)
=          : (15, 0)
a          : (3, 1)
/          : (13, 0)
b          : (3, 2)
;          : (37, 0)
}          : (33, 0)

 symbol table ----
{'a': 1, 'b': 2, '_asdf': 3}

```
<br>

## 개발 후기

토큰 중에서 까다로웠던 것은 따옴표 (‘, ’) 와 관련된 부분이었습니다. 그 자체로 토큰이면서, 동시에 상수를 구별하기 위한 문자였기 때문에, 하나의 DFA 경로에서 토큰이 여러 개 출력되게끔 만들어야 해서 생각보다 시간이 걸렸던 것 같습니다. Token 탐색 부분의 구현에서는 이전의 DFA 과제에서 graph를 만들었던 기억을 살려 비슷하게 구현하였는데, 이 과정에서 실제 스캐너 수준의 프로그램을 만들 때는 어떤 방식으로 state diagram 을 구현하는 것이 효율적인지 궁금해졌습니다.  <br>

참고할 오픈소스가 있어서 전체적인 구성에서는 비교적 수월하게 코드를 짤 수 있었으나, 상수나 실수와 같이 새로 추가해야 하는 요소를 어떻게 깔끔하게 넣을 수 있는지에 대해서 고민을 많이 해야 했습니다.  <br>

프로젝트를 하면서 Enum 클래스 활용 등 새로 알게 된 것이 있었으나, state 나 symbol table 구현에 dictionary 와 string 을 위주로 활용하게 되면서 getToken(), setSymbol() 와 같이 핵심 로직이 있는 메소드에 문자열이 너무 많이 들어간(하드 코딩 된) 것 같아 아쉽습니다.  <br>

이번에 코드를 짜면서 클래스 설계에 대해서 다시 공부할 필요성을 느꼈습니다. (ex. 메소드와 속성을 효율적으로 나누는 법). 이번에는 코드의 완성에 초점을 맞췄는데, 추후에 다시 코드를 보면서 개선첨을 생각해보는 것도 좋을 것 같습니다.  <br>
