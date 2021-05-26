import dash_html_components as html


class Error404View:
    @staticmethod
    def make_layout() -> html.Div:
        return html.Div(
            children=[html.H1(children="404 no such page", style={"textAlign": "center", "marginBottom": 50})],
        )
