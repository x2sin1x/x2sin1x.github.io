/**
 * 原样内容容器插件：提供与主题 imgCard / note 等一致的 ::: 容器语法，
 * 但容器内容不做任何 markdown 解析、原样提取（与 ``` 围栏行为一致），
 * 适用于 mermaid / abcjs 等代码型内容。
 *
 * 为什么不直接用 markdown-it-container（主题 note/imgCard 的底层插件）：
 * 它会把容器内容当作 markdown 解析，图表源码中的 ---、# 标题、
 * 4 空格缩进（列表/代码块）、空行分段等都会破坏源码的原样性。
 * 本插件的块规则参考 markdown-it-container 的实现，只复用 ::: 语法并提取原文。
 *
 * 类型说明：markdown-it 是 vitepress-theme-teek 的传递依赖、未在顶层安装，
 * 其 StateBlock 等类型无法直接引用，这里按实际用到的成员做结构化类型定义；
 * VitePress 传入的 MarkdownRenderer 可结构化匹配。
 */

interface RawContainerToken {
  content: string;
  map: number[] | null;
}

interface RawContainerState {
  src: string;
  bMarks: number[];
  eMarks: number[];
  tShift: number[];
  blkIndent: number;
  line: number;
  push(type: string, tag: string, nesting: number): RawContainerToken;
  getLines(begin: number, end: number, indent: number, keepBlankLines: boolean): string;
}

export interface RawContainerMarkdownIt {
  block: {
    ruler: {
      before(
        beforeName: string,
        ruleName: string,
        rule: (state: RawContainerState, startLine: number, endLine: number, silent: boolean) => boolean,
      ): void;
    };
  };
}

const COLON = 0x3a; // ":"
const SPACE = 0x20; // " "

/**
 * 注册一个 ::: name ... ::: 原样内容容器。
 * 标准语法要求冒号与容器名之间有一个空格（::: mermaid），不带空格的写法不识别，
 * 以便误写时直接暴露为普通文本而非静默渲染
 * @param render 收到原样源码，返回插入页面的 HTML（如组件标签）
 */
export function useRawContainer(
  md: RawContainerMarkdownIt,
  name: string,
  render: (source: string) => string,
): void {
  md.block.ruler.before("fence", `raw_container_${name}`, (state, startLine, endLine, silent) => {
    // 行索引由 markdown-it 保证落在有效范围内，越界回退 0 不会影响正确性
    const at = (arr: number[], index: number): number => arr[index] ?? 0;

    const openLineStart = at(state.bMarks, startLine) + at(state.tShift, startLine);
    const max = at(state.eMarks, startLine);
    let pos = openLineStart;

    // 打开行：至少 3 个冒号 + 空格 + 恰好为容器名的参数（如 ::: mermaid）
    if (pos >= max || state.src.charCodeAt(pos) !== COLON) return false;
    while (pos < max && state.src.charCodeAt(pos) === COLON) pos++;
    if (pos - openLineStart < 3) return false;
    // 冒号与容器名之间必须有空格；允许写多个空格（trim 归一）
    if (pos >= max || state.src.charCodeAt(pos) !== SPACE) return false;
    pos++;
    while (pos < max && state.src.charCodeAt(pos) === SPACE) pos++;
    if (state.src.slice(pos, max).trim() !== name) return false;

    if (silent) return true;

    // 查找闭合行：只含至少 3 个冒号的行；未闭合则按普通文本处理
    let closeLine = -1;
    for (let line = startLine + 1; line < endLine; line++) {
      const lineStartOfClose = at(state.bMarks, line) + at(state.tShift, line);
      const m = at(state.eMarks, line);
      let p = lineStartOfClose;
      if (p >= m || state.src.charCodeAt(p) !== COLON) continue;
      while (p < m && state.src.charCodeAt(p) === COLON) p++;
      if (p - lineStartOfClose >= 3 && state.src.slice(p, m).trim() === "") {
        closeLine = line;
        break;
      }
    }
    if (closeLine === -1) return false;

    // 原样提取容器内容：不经 markdown 解析，按当前块级缩进剥离嵌套缩进
    const source = state.getLines(startLine + 1, closeLine, state.blkIndent, true).replace(/\n+$/, "");
    const token = state.push("html_block", "", 0);
    token.content = render(source);
    token.map = [startLine, closeLine + 1];
    state.line = closeLine + 1;
    return true;
  });
}
