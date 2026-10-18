// gohelper: Go source facts for testprune.
//
//	gohelper sites <file.go>   mutation sites in function bodies (JSON lines)
//	gohelper funcs <file.go>   function ranges (JSON lines)
//	gohelper tests <file.go>   test functions with their source (JSON lines)
package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"strconv"
	"strings"
)

type site struct {
	Line  int    `json:"line"`
	Start int    `json:"start"` // byte offsets in the file
	End   int    `json:"end"`
	Op    string `json:"op"`
	Orig  string `json:"orig"`
	Rep   string `json:"rep"`
}

var cmpFlip = map[token.Token]token.Token{token.EQL: token.NEQ, token.NEQ: token.EQL, token.LSS: token.GEQ,
	token.GEQ: token.LSS, token.GTR: token.LEQ, token.LEQ: token.GTR}
var arith = map[token.Token]token.Token{token.ADD: token.SUB, token.SUB: token.ADD, token.MUL: token.QUO, token.QUO: token.MUL}

func main() {
	if len(os.Args) != 3 {
		fmt.Fprintln(os.Stderr, "usage: gohelper sites|funcs|tests <file.go>")
		os.Exit(2)
	}
	src, err := os.ReadFile(os.Args[2])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fset := token.NewFileSet()
	f, err := parser.ParseFile(fset, os.Args[2], src, parser.ParseComments)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	enc := json.NewEncoder(os.Stdout)
	off := func(p token.Pos) int { return fset.Position(p).Offset }
	line := func(p token.Pos) int { return fset.Position(p).Line }
	switch os.Args[1] {
	case "funcs", "tests":
		for _, d := range f.Decls {
			fd, ok := d.(*ast.FuncDecl)
			if !ok || fd.Body == nil {
				continue
			}
			name := fd.Name.Name
			if fd.Recv != nil && len(fd.Recv.List) > 0 {
				name = recvName(fd.Recv.List[0].Type) + "." + name
			}
			if os.Args[1] == "tests" {
				if fd.Recv != nil || !strings.HasPrefix(fd.Name.Name, "Test") {
					continue
				}
				enc.Encode(map[string]any{"name": fd.Name.Name, "source": string(src[off(fd.Pos()):off(fd.End())])})
				continue
			}
			enc.Encode(map[string]any{"name": name, "start": line(fd.Pos()), "end": line(fd.End())})
		}
	case "sites":
		for _, d := range f.Decls {
			fd, ok := d.(*ast.FuncDecl)
			if !ok || fd.Body == nil {
				continue
			}
			ast.Inspect(fd.Body, func(n ast.Node) bool {
				emit := func(start, end token.Pos, op, rep string) {
					if line(start) != line(end) {
						return
					}
					enc.Encode(site{line(start), off(start), off(end), op, string(src[off(start):off(end)]), rep})
				}
				switch x := n.(type) {
				case *ast.BinaryExpr:
					opEnd := x.OpPos + token.Pos(len(x.Op.String()))
					if t, ok := cmpFlip[x.Op]; ok {
						emit(x.OpPos, opEnd, "cmp_flip", t.String())
					} else if t, ok := arith[x.Op]; ok && !isString(x) {
						emit(x.OpPos, opEnd, "arith_swap", t.String())
					} else if x.Op == token.LAND {
						emit(x.OpPos, opEnd, "andor_swap", "||")
					} else if x.Op == token.LOR {
						emit(x.OpPos, opEnd, "andor_swap", "&&")
					}
				case *ast.UnaryExpr:
					if x.Op == token.NOT {
						emit(x.OpPos, x.OpPos+1, "not_removal", "")
					}
				case *ast.Ident:
					if x.Name == "true" {
						emit(x.Pos(), x.End(), "bool_flip", "false")
					} else if x.Name == "false" {
						emit(x.Pos(), x.End(), "bool_flip", "true")
					}
				case *ast.BasicLit:
					if x.Kind == token.INT {
						if v, err := strconv.ParseInt(x.Value, 0, 64); err == nil {
							emit(x.Pos(), x.End(), "const_plus1", strconv.FormatInt(v+1, 10))
						}
					}
				}
				return true
			})
		}
	}
}

func recvName(e ast.Expr) string {
	switch t := e.(type) {
	case *ast.StarExpr:
		return recvName(t.X)
	case *ast.Ident:
		return t.Name
	case *ast.IndexExpr:
		return recvName(t.X)
	case *ast.IndexListExpr:
		return recvName(t.X)
	}
	return "?"
}

// isString guesses string concatenation (a literal string operand), where + cannot become -.
func isString(b *ast.BinaryExpr) bool {
	for _, e := range []ast.Expr{b.X, b.Y} {
		if l, ok := e.(*ast.BasicLit); ok && l.Kind == token.STRING {
			return true
		}
	}
	return false
}
