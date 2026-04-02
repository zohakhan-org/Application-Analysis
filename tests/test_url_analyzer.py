from app_analysis_framework.analyzers.url_analyzer import _SignalExtractor


def test_signal_extractor_parses_basic_tags():
    html = """
    <html>
      <head>
        <title>Demo</title>
        <meta name='description' content='sample'>
      </head>
      <body>
        <h1>Main</h1>
        <img src='a.jpg'>
        <a href='https://example.com/x'>Internal</a>
        <a href='https://other.com/y'>External</a>
      </body>
    </html>
    """
    parser = _SignalExtractor(domain="example.com")
    parser.feed(html)

    s = parser.signals
    assert s.title == "Demo"
    assert s.has_meta_description is True
    assert s.h1_count == 1
    assert s.images_missing_alt == 1
    assert s.internal_links == 1
    assert s.external_links == 1
