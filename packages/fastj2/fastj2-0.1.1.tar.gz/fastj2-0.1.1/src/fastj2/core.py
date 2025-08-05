from pathlib import Path
from typing import Callable, Optional

from jinja2 import Environment, FileSystemLoader
from loguru import logger as log
from starlette.responses import HTMLResponse
from toomanyconfigs import CWD
from toomanyconfigs.cwd import CWDNamespace


def default_error_method(e: Exception, template_name: str, context: dict) -> HTMLResponse:
    """Default error handler for template rendering failures"""
    import traceback

    # Generate context info
    context_info = ""
    for key, value in context.items():
        if isinstance(value, (dict, list)):
            context_info += f"<p><strong>{key}:</strong> {len(value)} items</p>\n"
        else:
            context_info += f"<p><strong>{key}:</strong> {str(value)[:100]}...</p>\n"

    fallback_html = f"""
    <html>
    <head><title>Template Error</title></head>
    <body>
        <h1>Template Rendering Error</h1>
        <p><strong>Template:</strong> {template_name}</p>
        <p><strong>Error:</strong> {str(e)}</p>
        
        <h3>Context Information</h3>
        {context_info}
        
        <details>
            <summary>Full Error Details</summary>
            <pre>{traceback.format_exc()}</pre>
        </details>
    </body>
    </html>
    """
    return HTMLResponse(fallback_html, status_code=500)


class FastJ2(CWD, Environment):
    templates: CWDNamespace

    def __init__(
        self,
        error_method: Optional[Callable[[Exception, str, dict], HTMLResponse]] = None,
        *cwd_args
    ):
        CWD.__init__(self, "templates/", *cwd_args)
        Environment.__init__(
            self,
            loader=FileSystemLoader(Path(self.templates._path))  # type: ignore
        )
        self.error_method = error_method or default_error_method
        log.success(f"{self}: Successfully initialized FastJ2 Templater for FastAPI with params:\n  - path={self.cwd}\n  - cwd_args={cwd_args}\n  - error_method={self.error_method}")

    def __repr__(self):
        return f"[FastJ2.{self.cwd.name}]"

    def safe_render(self, template_name: str, **context) -> HTMLResponse:
        """
        Safely render a template with comprehensive error handling and fallback.

        Args:
            template_name: Name of the template file to render
            **context: Template context variables

        Returns:
            HTMLResponse with rendered template or fallback HTML
        """
        try:
            template = self.get_template(template_name)
            log.debug(f"About to render template: {template_name}")
            rendered_html = template.render(**context)
            log.debug(f"Template {template_name} rendered successfully")
            return HTMLResponse(rendered_html)

        except Exception as e:
            import traceback
            full_traceback = traceback.format_exc()
            log.error(f"{self}: Exception rendering template '{template_name}': {type(e).__name__}: {e}\n{full_traceback}\nTemplate context: {context}")
            return self.error_method(e, template_name, context)

    def safe_render_string(self, template_string: str, **context) -> HTMLResponse:
        """Render a template from string with safe error handling"""
        try:
            template = self.from_string(template_string)
            rendered_html = template.render(**context)
            log.debug("String template rendered successfully")
            return HTMLResponse(rendered_html)
        except Exception as e:
            log.error(f"Exception rendering string template: {type(e).__name__}: {e}")
            return self.error_method(e, "string_template", context)