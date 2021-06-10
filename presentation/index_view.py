import dash_core_components as dcc
import dash_html_components as html


class IndexView:
    """ Represents the main page template; header, footer, content place holder """

    URL = "url"
    REDIRECT = "hidden_div_for_redirect_callback"
    PAGE_CONTENT = "page-content"

    @staticmethod
    def make_layout() -> html.Div:
        # TODO: add page header
        # TODO: add page footer
        return html.Div(
            [
                # doesn't render anything, enables redirections
                html.Div(id=IndexView.REDIRECT),
                # doesn't render anything, represents the URL bar
                dcc.Location(id=IndexView.URL, refresh=False),
                # content will be rendered in this element,
                dcc.Loading(
                    id=IndexView.PAGE_CONTENT,
                    type="default",
                    fullscreen=True,
                ),
            ]
        )
