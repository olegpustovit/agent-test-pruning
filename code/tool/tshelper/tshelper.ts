// tshelper: static facts about a TypeScript repository for ts_adapter.py, using the oxc parser from the repo's node_modules.
//   bun run tshelper.ts graph <repo> <entry>...   JSON line per entry: {entry, files: [repo-relative local files reached]}
//   bun run tshelper.ts funcs <repo> <file>...    JSON line per file: {file, funcs: [{name, kind, start, end}], body_lines: [..]}
//   bun run tshelper.ts sites <repo> <file>...    JSON line per mutation site: {file, line, start, end, op, orig, rep} (UTF-8 byte offsets)
//   bun run tshelper.ts check <repo> <file>       exit 1 when the file does not parse
// TypeScript 7 (the repo's compiler) ships no in-process parser API, so oxc-parser (also a repo devDependency) gives the AST.
import { existsSync, readFileSync, statSync, readdirSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';

const [cmd, repoArg, ...rest] = process.argv.slice(2);
const repo = resolve(repoArg!);
const parserRoot = process.env.TSHELPER_PARSER_REPO ?? repo;
const { parseSync } = await import(join(parserRoot, 'node_modules/oxc-parser/src-js/index.js'));

type Node = { type: string; start: number; end: number; [k: string]: any };

function parse(abs: string, src: string) {
  return parseSync(abs, src, { sourceType: 'module', preserveParens: true });
}

const SKIP_KEYS = new Set(['typeAnnotation', 'returnType', 'typeParameters', 'typeArguments', 'superTypeArguments', 'decorators']);
const TYPE_ONLY = new Set(['TSTypeAliasDeclaration', 'TSInterfaceDeclaration', 'TSLiteralType', 'TSDeclareFunction', 'TSModuleDeclaration']);

function children(node: Node): Node[] {
  const out: Node[] = [];
  for (const [k, v] of Object.entries(node)) {
    if (SKIP_KEYS.has(k)) continue;
    if (Array.isArray(v)) { for (const c of v) if (c && typeof c === 'object' && typeof c.type === 'string') out.push(c); }
    else if (v && typeof v === 'object' && typeof (v as Node).type === 'string') out.push(v as Node);
  }
  return out;
}

// ---------- module graph ----------

const EXTS = ['.ts', '.tsx', '.mts', '.cts', '.js', '.jsx', '.mjs'];
const aliases: [string, string[]][] = [];
const workspaces = new Map<string, string>();
(function loadAliases() {
  try {
    const raw = readFileSync(join(repo, 'tsconfig.json'), 'utf8').replace(/^\s*\/\/.*$/gm, '');
    const co = JSON.parse(raw).compilerOptions ?? {};
    const base = resolve(repo, co.baseUrl ?? '.');
    for (const [k, vs] of Object.entries(co.paths ?? {})) aliases.push([k, (vs as string[]).map((v) => resolve(base, v))]);
  } catch { /* no tsconfig paths */ }
  try {
    const pkg = JSON.parse(readFileSync(join(repo, 'package.json'), 'utf8'));
    const ws: string[] = Array.isArray(pkg.workspaces) ? pkg.workspaces : pkg.workspaces?.packages ?? [];
    for (const pat of ws) {
      const dirs = pat.endsWith('/*') ? readdirSync(join(repo, pat.slice(0, -2))).map((d) => join(repo, pat.slice(0, -2), d)) : [join(repo, pat)];
      for (const d of dirs) {
        try { workspaces.set(JSON.parse(readFileSync(join(d, 'package.json'), 'utf8')).name, d); } catch { /* not a package */ }
      }
    }
  } catch { /* no workspaces */ }
})();

function isFile(p: string) { try { return statSync(p).isFile(); } catch { return false; } }

function tryPath(base: string): string | null {
  if (isFile(base) && EXTS.some((e) => base.endsWith(e))) return base;
  const m = base.match(/\.(m|c)?jsx?$/);
  if (m) {
    const stem = base.slice(0, -m[0].length);
    for (const e of ['.ts', '.tsx', '.mts', '.cts']) if (isFile(stem + e)) return stem + e;
  }
  for (const e of EXTS) if (isFile(base + e)) return base + e;
  for (const e of EXTS) if (isFile(join(base, 'index' + e))) return join(base, 'index' + e);
  return null;
}

function resolveSpec(fromAbs: string, spec: string): string | null {
  let hit: string | null = null;
  if (spec.startsWith('.') || spec.startsWith('/')) hit = tryPath(resolve(dirname(fromAbs), spec));
  else {
    for (const [k, targets] of aliases) {
      const star = k.indexOf('*');
      if (star < 0 ? spec === k : spec.startsWith(k.slice(0, star)) && spec.endsWith(k.slice(star + 1))) {
        const mid = star < 0 ? '' : spec.slice(star, spec.length - (k.length - star - 1));
        for (const t of targets) { hit = tryPath(t.replace('*', mid)); if (hit) break; }
        if (hit) break;
      }
    }
    if (!hit) {
      for (const [name, dir] of workspaces) {
        if (spec === name) { hit = tryPath(join(dir, 'src/index')) ?? tryPath(join(dir, 'index')); break; }
        if (spec.startsWith(name + '/')) { hit = tryPath(join(dir, spec.slice(name.length + 1))); break; }
      }
    }
  }
  if (!hit) return null;
  const rel = relative(repo, hit);
  if (rel.startsWith('..') || rel.split('/').includes('node_modules')) return null;
  return hit;
}

const importCache = new Map<string, string[]>();
function importsOf(abs: string): string[] {
  const cached = importCache.get(abs);
  if (cached) return cached;
  const specs: string[] = [];
  try {
    const src = readFileSync(abs, 'utf8');
    const r = parse(abs, src);
    const walk = (n: Node) => {
      switch (n.type) {
        case 'ImportDeclaration':
          if (n.importKind !== 'type') specs.push(n.source.value);
          return;
        case 'ExportNamedDeclaration':
        case 'ExportAllDeclaration':
          if (n.source && n.exportKind !== 'type') specs.push(n.source.value);
          break;
        case 'ImportExpression':
          if (n.source?.type === 'Literal' && typeof n.source.value === 'string') specs.push(n.source.value);
          break;
        case 'CallExpression':
          if (n.callee?.type === 'Identifier' && n.callee.name === 'require' && n.arguments?.[0]?.type === 'Literal' && typeof n.arguments[0].value === 'string') specs.push(n.arguments[0].value);
          break;
        case 'TSImportEqualsDeclaration':
          if (n.importKind !== 'type' && n.moduleReference?.type === 'TSExternalModuleReference') specs.push(n.moduleReference.expression.value);
          return;
      }
      for (const c of children(n)) walk(c);
    };
    walk(r.program);
  } catch { /* unreadable file: no edges */ }
  const out = [...new Set(specs.map((s) => resolveSpec(abs, s)).filter((x): x is string => x !== null))];
  importCache.set(abs, out);
  return out;
}

function graph(entry: string): string[] {
  const start = resolve(repo, entry);
  const seen = new Set<string>([start]);
  const stack = [start];
  while (stack.length) for (const d of importsOf(stack.pop()!)) if (!seen.has(d)) { seen.add(d); stack.push(d); }
  return [...seen].map((p) => relative(repo, p)).sort();
}

// ---------- functions and mutation sites ----------

function keyName(k: Node | undefined, computed: boolean): string {
  if (!k) return '?';
  if (computed) return '[computed]';
  if (k.type === 'Identifier') return k.name;
  if (k.type === 'PrivateIdentifier') return '#' + k.name;
  if (k.type === 'Literal') return String(k.value);
  return '?';
}

const FN = new Set(['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']);

type Fn = { name: string; kind: string; start: number; end: number; s: number; e: number };

function lineIndex(src: string) {
  const starts = [0];
  for (let i = 0; i < src.length; i++) if (src.charCodeAt(i) === 10) starts.push(i + 1);
  return (off: number) => {
    let lo = 0, hi = starts.length - 1;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (starts[mid]! <= off) lo = mid; else hi = mid - 1; }
    return lo + 1;
  };
}

function analyze(abs: string) {
  const src = readFileSync(abs, 'utf8');
  const r = parse(abs, src);
  const line = lineIndex(src);
  const ascii = Buffer.byteLength(src) === src.length;
  const byte = (off: number) => (ascii ? off : Buffer.byteLength(src.slice(0, off)));
  const fns: Fn[] = [];
  const sites: any[] = [];
  const used = new Map<string, number>();
  const uniq = (n: string, l: number) => { const c = used.get(n) ?? 0; used.set(n, c + 1); return c ? `${n}@${l}` : n; };
  const add = (name: string, kind: string, n: Node) => {
    const l = line(n.start);
    const full = uniq(name, l);
    fns.push({ name: full, kind, start: l, end: line(Math.max(n.end - 1, n.start)), s: n.start, e: n.end });
    return full;
  };
  const site = (start: number, end: number, op: string, rep: string) => {
    sites.push({ line: line(start), start: byte(start), end: byte(end), op, orig: src.slice(start, end), rep });
  };
  const isStr = (n: Node): boolean => {
    let x = n;
    while (x.type === 'ParenthesizedExpression') x = x.expression;
    if (x.type === 'TemplateLiteral' || (x.type === 'Literal' && typeof x.value === 'string')) return true;
    if (x.type === 'BinaryExpression' && x.operator === '+') return isStr(x.left) || isStr(x.right);
    return false;
  };
  const opSite = (n: Node, op: string, rep: string, kind: string) => {
    const gap = src.slice(n.left.end, n.right.start);
    const i = gap.indexOf(op);
    if (i >= 0) site(n.left.end + i, n.left.end + i + op.length, kind, rep);
  };
  const CMP: Record<string, string> = { '===': '!==', '!==': '===', '==': '!=', '!=': '==', '<': '>=', '>=': '<', '>': '<=', '<=': '>' };
  const ARITH: Record<string, string> = { '+': '-', '-': '+', '*': '/', '/': '*' };

  const walk = (n: Node, prefix: string, inFn: boolean, hint: string | null) => {
    if (TYPE_ONLY.has(n.type)) return;
    let p = prefix;
    let fn = inFn;
    if (FN.has(n.type) && n.body) {
      const nm = n.id?.name ?? hint ?? (n.type === 'FunctionDeclaration' ? 'default' : `anonymous@${line(n.start)}`);
      // anonymous callbacks inside a named function belong to it; they are not symbols of their own
      if (!(inFn && !n.id && !hint)) p = add(prefix + nm, 'function', n) + '.';
      fn = true;
    } else if (n.type === 'ClassDeclaration' || n.type === 'ClassExpression') {
      p = add(prefix + (n.id?.name ?? hint ?? `class@${line(n.start)}`), 'class', n) + '.';
    }
    if (fn) {
      if (n.type === 'BinaryExpression') {
        if (CMP[n.operator]) opSite(n, n.operator, CMP[n.operator]!, 'cmp');
        else if (ARITH[n.operator] && !isStr(n.left) && !isStr(n.right)) opSite(n, n.operator, ARITH[n.operator]!, 'arith');
      } else if (n.type === 'LogicalExpression' && (n.operator === '&&' || n.operator === '||')) {
        opSite(n, n.operator, n.operator === '&&' ? '||' : '&&', 'logic');
      } else if (n.type === 'UnaryExpression' && n.operator === '!') {
        site(n.start, n.argument.start, 'not', '');
      } else if (n.type === 'Literal' && typeof n.value === 'boolean') {
        site(n.start, n.end, 'bool', n.value ? 'false' : 'true');
      } else if (n.type === 'Literal' && typeof n.value === 'number' && Number.isFinite(n.value) && Math.abs(n.value) < 2 ** 52) {
        site(n.start, n.end, 'num', String(n.value + 1));
      }
    }
    for (const [k, v] of Object.entries(n)) {
      if (SKIP_KEYS.has(k)) continue;
      const kids = Array.isArray(v) ? v : [v];
      for (const c of kids) {
        if (!c || typeof c !== 'object' || typeof c.type !== 'string') continue;
        let h: string | null = null;
        if ((n.type === 'VariableDeclarator') && k === 'init' && n.id?.type === 'Identifier') h = n.id.name;
        else if ((n.type === 'MethodDefinition' || n.type === 'TSAbstractMethodDefinition') && k === 'value') h = (n.kind === 'get' || n.kind === 'set' ? n.kind + ' ' : '') + keyName(n.key, n.computed);
        else if ((n.type === 'PropertyDefinition' || n.type === 'Property') && k === 'value') h = keyName(n.key, n.computed);
        else if (n.type === 'AssignmentExpression' && k === 'right' && n.left?.type === 'Identifier') h = n.left.name;
        else if (n.type === 'ExportDefaultDeclaration') h = 'default';
        // an object literal bound to a name prefixes its function-valued properties
        if ((n.type === 'VariableDeclarator') && k === 'init' && c.type === 'ObjectExpression' && h && !fn) {
          walk(c, p + h + '.', fn, null);
          continue;
        }
        walk(c, p, fn, FN.has(c.type) || c.type === 'ClassExpression' ? h : null);
      }
    }
  };
  walk(r.program, '', false, null);
  return { fns, sites, src };
}

function out(o: unknown) { process.stdout.write(JSON.stringify(o) + '\n'); }

if (cmd === 'graph') {
  for (const e of rest) out({ entry: e, files: graph(e) });
} else if (cmd === 'funcs') {
  for (const f of rest) {
    try {
      const { fns } = analyze(resolve(repo, f));
      const body = new Set<number>();
      for (const x of fns) if (x.kind === 'function') for (let l = x.start; l <= x.end; l++) body.add(l);
      out({ file: f, funcs: fns.map(({ name, kind, start, end }) => ({ name, kind, start, end })), body_lines: [...body].sort((a, b) => a - b) });
    } catch (err) { out({ file: f, funcs: [], body_lines: [], error: String(err) }); }
  }
} else if (cmd === 'sites') {
  for (const f of rest) {
    try { for (const s of analyze(resolve(repo, f)).sites) out({ file: f, ...s }); } catch { /* unparsable file: no sites */ }
  }
} else if (cmd === 'check') {
  const abs = resolve(repo, rest[0]!);
  const r = parse(abs, readFileSync(abs, 'utf8'));
  process.exit(r.errors.length ? 1 : 0);
} else {
  console.error('usage: tshelper.ts graph|funcs|sites|check <repo> <files...>');
  process.exit(2);
}
