# src/report_generator.py
import logging
logging.getLogger("weasyprint").setLevel(logging.ERROR)

import json
from pathlib import Path
from datetime import datetime
from jinja2 import Template
import weasyprint

TEMPLATE_MD = """
# Executive Market Intelligence Report
Generated: {{ generated_at }}

## Top Categories
{% for ins in insights[:6] %}
### {{ loop.index }}. {{ ins.category }} (confidence: {{ ins.confidence }})
- Apps: {{ ins.metrics.apps }}
- Avg rating: {{ ins.metrics.avg_rating }}
- Median price: {{ ins.metrics.median_price }}
**Recommendations**
{% if ins.llm.recommendations %}
{% for r in ins.llm.recommendations %}
- {{ r }}
{% endfor %}
{% else %}
- {{ ins.llm.raw | default('See LLM content') }}
{% endif %}
{% endfor %}
"""

def render_report(insights_debug_json='outputs/insights_debug.json',
                  out_md='outputs/report.md',
                  out_pdf='outputs/report.pdf'):
    # Load JSON insights
    data = json.load(open(insights_debug_json))
    generated_at = data.get('generated_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    insights = data.get('insights', [])

    # Render Markdown with Jinja2
    t = Template(TEMPLATE_MD)
    md = t.render(generated_at=generated_at, insights=insights)
    Path(out_md).write_text(md)

    # Render PDF with embedded sans-serif font to avoid Fontconfig warnings
    css = weasyprint.CSS(string="""
    @page { size: A4; margin: 1cm; }
    body { font-family: sans-serif; }
    h1,h2,h3 { font-family: sans-serif; }
    """)
    html = weasyprint.HTML(string=md)
    html.write_pdf(out_pdf, stylesheets=[css])

    print("Saved:", out_md, out_pdf)

if __name__ == '__main__':
    render_report()
