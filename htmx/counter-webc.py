from fasthtml.common import *
from fasthtml.components import X_incrementer

app,rt = fast_app(live=True)

js = """
import {LitElement, html, css} from "https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js";

class Incrementer extends LitElement {
  static styles = css`button { margin: 6px; }`;
  render() {
    return html`
      <output><slot></slot></output>
      <button @click=${() => this.textContent++}>Increment</button>
    `;
  }
}

customElements.define('x-incrementer', Incrementer);"""

@rt
def index():
    return Titled('Web component counter',
        Script(js, type='module'),
        X_incrementer('0'),
        X_incrementer('5')
    )

serve()

