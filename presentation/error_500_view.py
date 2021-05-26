import dash_html_components as html


class Error500View:
    @staticmethod
    def make_layout() -> html.Div:
        return html.Div(
            children=[html.H1(children="500 internal server error", style={"textAlign": "center", "marginBottom": 50})],
        )
