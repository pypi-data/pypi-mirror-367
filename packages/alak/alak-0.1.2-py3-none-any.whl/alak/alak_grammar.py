grammar = r"""
start: statement+

statement: print_stmt
         | assign_stmt
         | if_stmt
         | while_stmt
         | func_def
         | func_call
         | hangover_stmt
         | patay_stmt
         | method_call_expr ";"

print_stmt: "tungga" expr ";"
assign_stmt: "alak" CNAME "=" expr ";"
if_stmt: "kung" "(" condition ")" "tagay" statement+ "bitaw"
while_stmt: "ikot" "(" condition ")" "tagay" statement+ "bitaw"

func_def: "inom" CNAME "(" [params] ")" "tagay" statement+ "bitaw"
params: CNAME ("," CNAME)*

hangover_stmt: "hangOver" assign_stmt condition ";" step_expr "tagay" statement+ "bitaw"
step_expr: CNAME "=" expr
assign_expr: "alak" CNAME "=" expr

func_call: CNAME "(" [args] ")" ";"
args: expr ("," expr)*

patay_stmt: "patayNa" "(" ")" ";"

condition: expr comp_op expr

?expr: expr "+" term   -> add
     | expr "-" term   -> sub
     | term

?term: term "*" factor -> mul
     | term "/" factor -> div
     | factor

?factor: method_call
       | method_call_expr
       | haba_expr
       | taas_expr
       | ambag_expr
       | list_literal
       | index_access
       | NUMBER        -> number
       | STRING        -> string
       | "walangTama"  -> false
       | "myTama"      -> true
       | CNAME         -> var
       | "(" expr ")"

list_literal: "[" [expr_list] "]"
expr_list: expr ("," expr)*

index_access: CNAME "[" expr "]"

haba_expr: "haba" "(" expr ")"
taas_expr: "taasTagay" "(" expr ")"
ambag_expr: "ambag" "(" expr ")"
method_call_expr: CNAME "." CNAME "(" [args] ")"
method_call: CNAME "(" [expr_list] ")"

comp_op: "==" | "!=" | ">" | "<"

%import common.CNAME
%import common.NUMBER
%import common.ESCAPED_STRING -> STRING
%import common.WS
%ignore WS

SL_COMMENT: /\/\/[^\r\n]*/
%ignore SL_COMMENT
"""