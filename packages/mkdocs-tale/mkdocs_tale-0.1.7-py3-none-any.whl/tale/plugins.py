from mkdocs.plugins import BasePlugin
from jinja2 import Environment
from datetime import datetime
from .filters import FILTERS
from .utils import purify_date
import logging

log = logging.getLogger("mkdocs.tale")

class TalePlugin(BasePlugin):
    
    def on_env(self, env: Environment, config, files):
        for name, fn in FILTERS.items():
            env.filters[name] = fn
        return env

    def on_config(self, config):
        config.extra["tale_pages"] = []
        return config
    
    def on_page_markdown(self, markdown, page, config, files):
        page_date = page.meta.get("date", None)
        d = purify_date(page_date)
        page.date = d.strftime('%Y-%m-%d') if d else ""
        config.extra["tale_pages"].append(page)
        log.debug(f"page name: {page.file}")
        return markdown

    def on_post_build(self, config):
        """排序逻辑执行完毕"""
        # config.extra["tale_pages"].sort(key=lambda x: x[1], reverse=True)
        return config