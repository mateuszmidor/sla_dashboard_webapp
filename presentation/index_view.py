from dash import dcc, html


class IndexView:
    """Represents the main page template; header, footer, content place holder"""

    URL = "url"
    PAGE_CONTENT = "page-content"
    MATRIX_REDIRECT = "matrix-click-redirect"
    METRIC_REDIRECT = "metric-selector-redirect"
    DISREGARD_AUTO_REFRESH_OUTPUT = "disregard_auto-refresh-output"  # need to store callback output somewhere

    @staticmethod
    def make_layout() -> html.Div:
        return html.Div(
            [
                # doesn't render anything, represents the URL bar
                dcc.Location(id=IndexView.URL, refresh=False),
                # doesn't render anything, enables redirections
                html.Div(id=IndexView.MATRIX_REDIRECT),
                html.Div(id=IndexView.METRIC_REDIRECT),
                html.Div(id=IndexView.DISREGARD_AUTO_REFRESH_OUTPUT),
                # content will be rendered in this element
                dcc.Loading(
                    id=IndexView.PAGE_CONTENT,
                    type="default",
                    fullscreen=True,
                ),
            ]
        )
