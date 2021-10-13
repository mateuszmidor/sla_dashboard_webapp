from dash import html


class HTTPErrorView:
    ERROR_MESSAGE = {404: "404 Page not found", 500: "500 Internal server error"}

    @classmethod
    def make_layout(cls, http_code: int) -> html.Div:
        return html.Div(
            children=[
                html.H1(children=cls.ERROR_MESSAGE[http_code], className="http_error_message"),
            ],
        )
