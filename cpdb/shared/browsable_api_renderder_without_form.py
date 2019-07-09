from rest_framework.renderers import BrowsableAPIRenderer


class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """Renders the browsable api, but excludes the forms."""
    def get_rendered_html_form(self, *args, **kwargs):
        """
        We don't want the HTML forms to be rendered because it can be
        really slow with large datasets
        """
        return ""
