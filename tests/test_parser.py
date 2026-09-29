from app.services.parser import parse_html

def test_parse_html_extracts_core_content():
    html = """
    <html>
      <head>
        <title>Example Article</title>
        <meta name="description" content="A useful description">
        <link rel="canonical" href="/article">
      </head>
      <body>
        <nav>Noise</nav>
        <article>
          <h1>Hello</h1>
          <p>This is useful article content.</p>
          <script>ignore_me()</script>
        </article>
      </body>
    </html>
    """
    page = parse_html(html, "https://example.com/x")
    assert page.title == "Example Article"
    assert page.description == "A useful description"
    assert page.canonical_url == "https://example.com/article"
    assert "useful article content" in page.text
    assert "ignore_me" not in page.text
