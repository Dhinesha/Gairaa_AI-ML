"""
Flow graph generator – converts Python AST into React Flow nodes and edges.
"""
import ast
import uuid
from typing import Any, Dict, List, Tuple


def _uid(prefix: str = "n") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class FlowGraphBuilder(ast.NodeVisitor):
    def __init__(self, source_lines: List[str]):
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self.source_lines = source_lines
        self._prev_ids: List[str] = []  # stack of "current tail" node ids

    def _add_node(self, node_type: str, label: str, line: int = None,
                  data: Dict = None) -> str:
        nid = _uid()
        self.nodes.append({
            "id": nid,
            "type": node_type,
            "label": label,
            "line": line,
            "data": data or {},
        })
        return nid

    def _connect(self, src: str, tgt: str, label: str = None, animated: bool = False):
        eid = f"e_{src}_{tgt}"
        self.edges.append({
            "id": eid,
            "source": src,
            "target": tgt,
            "label": label,
            "animated": animated,
        })

    def _src(self, lineno: int) -> str:
        if lineno and 1 <= lineno <= len(self.source_lines):
            return self.source_lines[lineno - 1].strip()
        return ""

    def build(self, tree: ast.AST) -> Dict[str, Any]:
        # Start node
        start_id = self._add_node("start", "▶ Start")
        self._prev_ids = [start_id]

        for stmt in tree.body:
            self._process_stmt(stmt)

        # End node
        end_id = self._add_node("end", "⏹ End")
        for prev in self._prev_ids:
            self._connect(prev, end_id)

        return {"nodes": self.nodes, "edges": self.edges}

    def _process_stmt(self, stmt: ast.stmt) -> List[str]:
        """Process a statement, connect from _prev_ids, return new tail ids."""
        lineno = getattr(stmt, "lineno", None)
        src = self._src(lineno) if lineno else ""

        if isinstance(stmt, ast.FunctionDef):
            nid = self._add_node("function_call", f"def {stmt.name}()", lineno)
            for prev in self._prev_ids:
                self._connect(prev, nid)
            self._prev_ids = [nid]

        elif isinstance(stmt, ast.If):
            cond_text = ast.unparse(stmt.test)
            cond_id = self._add_node("condition", f"if {cond_text}?", lineno,
                                      {"condition": cond_text})
            for prev in self._prev_ids:
                self._connect(prev, cond_id)

            # True branch
            self._prev_ids = [cond_id]
            for s in stmt.body:
                self._process_stmt(s)
            true_tails = list(self._prev_ids)

            # False branch
            false_tails = []
            if stmt.orelse:
                self._prev_ids = [cond_id]
                for s in stmt.orelse:
                    self._process_stmt(s)
                false_tails = list(self._prev_ids)
            else:
                false_tails = [cond_id]

            # Connect true branch
            for prev in [cond_id]:
                for t in true_tails:
                    pass  # already connected by recursion

            self._prev_ids = true_tails + false_tails

        elif isinstance(stmt, ast.For):
            iter_text = ast.unparse(stmt.iter)
            target_text = ast.unparse(stmt.target)
            loop_id = self._add_node("loop",
                                      f"for {target_text} in {iter_text}", lineno,
                                      {"type": "for", "target": target_text,
                                       "iter": iter_text})
            for prev in self._prev_ids:
                self._connect(prev, loop_id)
            self._prev_ids = [loop_id]
            for s in stmt.body:
                self._process_stmt(s)
            # Back edge to loop
            for tail in self._prev_ids:
                self._connect(tail, loop_id, "next iter", animated=True)
            self._prev_ids = [loop_id]

        elif isinstance(stmt, ast.While):
            cond_text = ast.unparse(stmt.test)
            loop_id = self._add_node("loop", f"while {cond_text}", lineno,
                                      {"type": "while", "condition": cond_text})
            for prev in self._prev_ids:
                self._connect(prev, loop_id)
            self._prev_ids = [loop_id]
            for s in stmt.body:
                self._process_stmt(s)
            for tail in self._prev_ids:
                self._connect(tail, loop_id, "loop", animated=True)
            self._prev_ids = [loop_id]

        elif isinstance(stmt, ast.Return):
            ret_text = ast.unparse(stmt.value) if stmt.value else "None"
            nid = self._add_node("return", f"return {ret_text}", lineno)
            for prev in self._prev_ids:
                self._connect(prev, nid)
            self._prev_ids = [nid]

        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call_text = ast.unparse(stmt.value)
            is_print = (isinstance(stmt.value.func, ast.Name)
                        and stmt.value.func.id == "print")
            node_type = "output" if is_print else "function_call"
            nid = self._add_node(node_type, call_text, lineno)
            for prev in self._prev_ids:
                self._connect(prev, nid)
            self._prev_ids = [nid]

        elif isinstance(stmt, ast.Assign):
            label = src or ast.unparse(stmt)
            nid = self._add_node("statement", label[:60], lineno)
            for prev in self._prev_ids:
                self._connect(prev, nid)
            self._prev_ids = [nid]

        else:
            label = src or type(stmt).__name__
            nid = self._add_node("statement", label[:60], lineno)
            for prev in self._prev_ids:
                self._connect(prev, nid)
            self._prev_ids = [nid]

        return self._prev_ids


def generate_flow(code: str) -> Dict[str, Any]:
    """Build a React Flow-compatible graph from Python source code."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        # Return minimal error graph
        err_id = _uid()
        end_id = _uid()
        return {
            "nodes": [
                {"id": "start", "type": "start", "label": "▶ Start", "line": None, "data": {}},
                {"id": err_id, "type": "error", "label": f"SyntaxError: {e.msg}", "line": e.lineno, "data": {}},
                {"id": "end", "type": "end", "label": "⏹ End", "line": None, "data": {}},
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": err_id, "label": None, "animated": False},
                {"id": "e2", "source": err_id, "target": "end", "label": None, "animated": False},
            ],
        }

    source_lines = code.splitlines()
    builder = FlowGraphBuilder(source_lines)
    return builder.build(tree)
