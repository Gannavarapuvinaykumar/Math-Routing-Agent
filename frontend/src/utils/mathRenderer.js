/**
 * Renders MathJax content when available
 */
export function renderMathJax() {
  if (typeof window !== 'undefined' && window.MathJax) {
    return window.MathJax.typesetPromise().catch((err) => {
      console.warn('MathJax rendering error:', err);
    });
  }
  return Promise.resolve();
}

/**
 * Converts plain text math notation to LaTeX format
 */
export function convertToLatex(content) {
  if (typeof content !== 'string') {
    return content;
  }

  return content
    .replace(/\^(\w+)/g, '^{$1}')        // x^2 -> x^{2}
    .replace(/\_(\w+)/g, '_{$1}')        // x_1 -> x_{1}
    .replace(/\bdx\b/g, '\\,dx')         // dx -> \,dx
    .replace(/\bdy\b/g, '\\,dy')         // dy -> \,dy
    .replace(/\bdt\b/g, '\\,dt')         // dt -> \,dt
    .replace(/\bdu\b/g, '\\,du')         // du -> \,du
    .replace(/\bdtheta\b/g, '\\,d\\theta') // dtheta -> \,d\theta
    .trim();
}

/**
 * Wraps math content for rendering (returns string, not JSX)
 */
export function wrapMathContent(content) {
  if (typeof content !== 'string') {
    return content;
  }

  return convertToLatex(content);
}

export default {
  renderMathJax,
  convertToLatex,
  wrapMathContent
};
