# Mini-C-Scanner_python
2021//11/24  
DKU – 오토마타와 컴파일러 : 스캐너 만들기  

## 기능에 대한 설명
**Mini C (C 언어의 일부 어휘를 가져온 가상의 언어) 를 대상으로 하는 스캐너 프로그램**  
**형식언어 – DFA Automata 를 기반으로 함.**  
> **스캐너(scanner) OR 어휘 분석기(lexical analyzer) 란** : 컴파일러의 일부로, 구문 분석기에서 호출하는 모듈.  
> 소스 프로그램을 읽어 토큰(token) 이라는 문법적으로 의미 있는 최소의 단위로 분리하는 것으로 토큰 스트림(stream) 을 출력함.  

**이때 토큰은 토큰번호(token number)와 토큰 값(token value)의 순서쌍으로 표현**  
**-> (토큰 번호, 토큰 값)**  <br><br>

스캐너 프로그램은 총 4가지 클래스로 구성함.
1.	MiniCScanner : 토큰 생성을 담당하는 클래스. 생성시 소스파일 경로를 입력 받으며, getToken 메소드를 실행할 때마다 토큰을 하나씩 반환함.
2.	LexicalError : Lexical Error 의 종류와 출력할 문자열이 들어있는 클래스.
3.	Token : MiniCScanner 에서 getToken 을 실행할 때마다 생성하는 token 객체 클래스. 
4.	SymbolTable : 사용자 정의어의 목록과 번호를 저장하는 테이블 클래스

## 각 토큰에 대한 설명 및 DFA
1. 주석문(Comment)  
  Block Comment (* ... *)
2. 사용자 정의어(Id)  
  첫글자는 _ 또는 영문자, 나머지는 영문자 숫자의 조합, no blank
  예약어(Reserved Word)는 제외
3. 상수  
  예) 숫자 상수 “10”, 문자 상수 “abc”
4. 정수  
  10진수(Decimal Number) : 0으로 시작하지 않는 일반 숫자. (eg. 526)
  8진수(Octal Number) : 0으로 시작하는 숫자. (eg. 0526)
  16진수(Hexa-decimal Number) : 0x로 시작하는 숫자 혹은 알파벳 AF.(1F) (eg. 0xFF, 0xff)
6. 실수  
  10.5, 13e+2, 20.3e-5
7. 예약어(Reserved words)  
  const, else, if, int, char, float return, void, while, for, break, continue
8 연산자(Operator)  
  사칙 연산자 : +, -, *, /, %
  배정 연산자 : =
  논리 연산자 : !, &&, ||
  관계 연산자 : ==, !=, <, >, <=, >=  
9 기호  
  대괄호('[', ']'), 중괄호('{', '}'), 소괄호('(', ')'), 컴마(','), 세미콜론(';').
  따옴표 (‘“’, ‘”,)
