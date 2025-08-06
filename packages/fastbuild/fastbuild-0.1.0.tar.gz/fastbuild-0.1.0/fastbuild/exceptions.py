# fastbuild/fastbuild/exceptions.py

class FastBuildError(Exception):
    """Exceção base para erros do FastBuild."""
    pass

class TemplateNotFoundError(FastBuildError):
    """Exceção para quando o diretório de templates não é encontrado."""
    pass

class SnippetNotFoundError(FastBuildError):
    def __init__(self, snippet_path):
        super().__init__(f"Snippet não encontrado: {snippet_path}")
