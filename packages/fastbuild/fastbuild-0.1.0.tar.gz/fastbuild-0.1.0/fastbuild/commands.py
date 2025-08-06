import os
import shutil
import subprocess
import click
from fastbuild.enum.package import DBPackages

def inject_snippet(file_path, snippet_path, marker, inside_class=False, inside_init_method=False):
    if not os.path.exists(snippet_path):
        click.secho(f"❌ Snippet não encontrado: {snippet_path}", fg="red")
        return

    with open(file_path, "r") as f:
        content = f.read()

    with open(snippet_path, "r") as f:
        snippet = f.read()

    if f"# BEGIN AUTO-INJECT:{marker}" in content:
        click.secho(f"⚠️ Já existe o bloco {marker} em {os.path.basename(file_path)}", fg="yellow")
        return

    block = f"# BEGIN AUTO-INJECT:{marker}\n{snippet}\n# END AUTO-INJECT:{marker}"

    if inside_init_method:
        if "def __init__" not in content:
            click.secho("❌ Método __init__ não encontrado para injeção.", fg="red")
            return

        lines = content.splitlines()
        new_lines = []
        inside_init = False
        for line in lines:
            new_lines.append(line)
            if "def __init__" in line and not inside_init:
                inside_init = True
            elif inside_init and line.strip() == "":
                indented = "\n".join(" " * 8 + l if l.strip() else "" for l in block.splitlines())
                new_lines.append(indented)
                inside_init = False
        new_content = "\n".join(new_lines)

    elif inside_class:
        if "class Configuration" not in content:
            click.secho("❌ Classe Configuration não encontrada para injeção.", fg="red")
            return
        new_content = content.replace(
            "class Configuration:",
            f"class Configuration:\n{block}"
        )

    else:
        new_content = content.strip() + f"\n\n{block}\n"

    with open(file_path, "w") as f:
        f.write(new_content)

    click.secho(f"✅ Código {marker} injetado em {os.path.basename(file_path)}", fg="green")


def update_requirements():
    try:
        result = subprocess.run(
            ["pip", "freeze"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        with open("requirements.txt", "w") as f:
            f.write(result.stdout)
        click.secho("📦 requirements.txt atualizado.", fg="cyan")
    except subprocess.CalledProcessError as e:
        click.secho(f"❌ Erro ao atualizar requirements.txt:\n{e.stderr}", fg="red")


def install_package(package_name):
    try:
        subprocess.run(["pip", "install", package_name], check=True)
        click.secho(f"✅ Pacote {package_name} instalado com sucesso", fg="green")
        return True
    except subprocess.CalledProcessError:
        click.secho(f"❌ Falha ao instalar pacote {package_name}", fg="red")
        return False


def uninstall_package(package_name):
    try:
        subprocess.run(["pip", "uninstall", "-y", package_name], check=True)
        click.secho(f"✅ Pacote {package_name} removido com sucesso", fg="green")
        return True
    except subprocess.CalledProcessError:
        click.secho(f"❌ Falha ao remover pacote {package_name}", fg="red")
        return False


@click.command(name="init-project", help="Cria estrutura base para projeto FastAPI.")
@click.option('--overwrite', is_flag=True, help="Sobrescreve a estrutura existente")
def init_project(overwrite):
    base_path = os.getcwd()
    template_path = os.path.join(os.path.dirname(__file__), "template", "default")

    if overwrite:
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        click.secho("🧹 Projeto limpo (overwrite).", fg="yellow")

    shutil.copytree(template_path, base_path, dirs_exist_ok=True)
    update_requirements()
    click.secho("✅ Projeto FastAPI inicializado com estrutura base!", fg="green")


@click.command(name="add-db", help="Adiciona módulo e configuração de banco de dados.")
def add_db():
    for pkg in DBPackages:
        if not install_package(pkg):
            return

    base_path = os.getcwd()
    db_template_path = os.path.join(os.path.dirname(__file__), "template", "database")
    snippets_path = os.path.join(os.path.dirname(__file__), "snippets")
    
    target_db_path = os.path.join(base_path, "src", "database")
    os.makedirs(target_db_path, exist_ok=True)

    for file_name in ["connection.py", "populate.py", "__init__.py"]:
        shutil.copyfile(
            os.path.join(db_template_path, file_name),
            os.path.join(target_db_path, file_name)
        )
    
    click.secho("📂 Módulo 'database' copiado para src/database/", fg="green")

    inject_snippet(
        file_path=os.path.join(base_path, "src", "__init__.py"),
        snippet_path=os.path.join(snippets_path, "init_import_snippet.py"),
        marker="DB_IMPORT",
        inside_class=False
    )

    inject_snippet(
        file_path=os.path.join(base_path, "src", "configuration", "settings.py"),
        snippet_path=os.path.join(snippets_path, "settings_db_vars.py"),
        marker="DB_SETTINGS",
        inside_init_method=True
    )

    inject_snippet(
        file_path=os.path.join(base_path, "src", "configuration", "settings.py"),
        snippet_path=os.path.join(snippets_path, "settings_db_methods.py"),
        marker="DB_METHODS",
        inside_class=False
    )

    update_requirements()
    click.secho("✅ Banco de dados configurado com sucesso!", fg="green", bold=True)


@click.command(name="remove-db", help="Remove o banco de dados e desfaz alterações.")
def remove_db():
    for pkg in DBPackages:
        uninstall_package(pkg)

    base_path = os.getcwd()
    db_path = os.path.join(base_path, "src", "database")
    init_path = os.path.join(base_path, "src", "__init__.py")
    settings_path = os.path.join(base_path, "src", "configuration", "settings.py")

    if os.path.exists(db_path):
        shutil.rmtree(db_path)
        click.secho("🗑️ Pasta src/database removida.", fg="yellow")

    def remove_injected_block(file_path, marker):
        with open(file_path, "r") as f:
            lines = f.readlines()

        inside_block = False
        cleaned_lines = []

        for line in lines:
            if f"# BEGIN AUTO-INJECT:{marker}" in line:
                inside_block = True
                continue
            if f"# END AUTO-INJECT:{marker}" in line:
                inside_block = False
                continue
            if not inside_block:
                cleaned_lines.append(line)

        with open(file_path, "w") as f:
            f.writelines(cleaned_lines)
        click.secho(f"🧹 Código {marker} removido de {os.path.basename(file_path)}", fg="cyan")

    remove_injected_block(init_path, "DB_IMPORT")
    remove_injected_block(settings_path, "DB_SETTINGS")
    remove_injected_block(settings_path, "DB_METHODS")

    update_requirements()
    click.secho("✅ Banco de dados removido com sucesso!", fg="green", bold=True)


@click.command(name="run-app", help="Roda a aplicação FastAPI (uvicorn ou python).")
@click.option("--uvicorn", is_flag=True, help="Usa o uvicorn para rodar o app")
def run_app(uvicorn):
    if uvicorn:
        click.secho("🚀 Rodando com uvicorn...", fg="cyan")
        subprocess.run(["uvicorn", "main:app", "--reload"])
    else:
        click.secho("🐍 Rodando com python main.py...", fg="cyan")
        subprocess.run(["python", "main.py"])
