import sqlite3
import json
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Scraping Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .page { border: 1px solid #ddd; margin: 20px 0; padding: 20px; }
        .url { color: #0066cc; font-weight: bold; }
        .title { font-size: 18px; margin: 10px 0; }
        .meta { color: #666; font-size: 12px; }
        .content { margin: 10px 0; max-height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>Scraping Results ({{ total }} pages)</h1>
    {% for page in pages %}
    <div class="page">
        <div class="url">{{ page.url }}</div>
        <div class="title">{{ page.title }}</div>
        <div class="meta">
            Status: {{ page.status_code }} | 
            Scraped: {{ page.scraped_at }} | 
            Links: {{ page.links_count }}
        </div>
        <div class="content">{{ page.content[:500] }}...</div>
    </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def view_results():
    conn = sqlite3.connect("scraped_pages.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT url, title, status_code, content, scraped_at, links 
        FROM scraped_pages 
        ORDER BY scraped_at DESC
    """)
    
    pages = []
    for row in cursor.fetchall():
        links_count = len(json.loads(row[5])) if row[5] else 0
        pages.append({
            'url': row[0],
            'title': row[1] or 'No Title',
            'status_code': row[2],
            'content': row[3] or '',
            'scraped_at': row[4],
            'links_count': links_count
        })
    
    conn.close()
    return render_template_string(HTML_TEMPLATE, pages=pages, total=len(pages))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    # Visit http://localhost:5000 to view results