import os
import sys

# Variáveis que o VS Code instalado via snap injeta no terminal/depurador.
# Elas apontam para bibliotecas do snap core20, e quando o Qt carrega o GTK
# acaba misturando a libpthread do snap com a glibc do sistema, gerando:
#   symbol lookup error: /snap/core20/.../libpthread.so.0: undefined symbol: __libc_pthread_init
SNAP_LEAKED_VARS = [
    "GTK_PATH", "GTK_EXE_PREFIX", "GTK_IM_MODULE_FILE",
    "GIO_MODULE_DIR", "GSETTINGS_SCHEMA_DIR",
    "GDK_PIXBUF_MODULE_FILE", "GDK_PIXBUF_MODULEDIR", "GDK_BACKEND",
    "LOCPATH", "XDG_DATA_HOME", "XDG_DATA_DIRS", "XDG_CONFIG_DIRS",
]


def _is_snap_path(value):
    return "/snap/" in value


def clean_snap_environment():
    """Remove do ambiente as variáveis herdadas do VS Code snap.

    Deve ser chamada antes de importar o PyQt5.
    """
    if not sys.platform.startswith("linux"):
        return

    for var in SNAP_LEAKED_VARS:
        orig_key = var + "_VSCODE_SNAP_ORIG"
        if orig_key in os.environ:
            # O VS Code snap guarda o valor original nessas variáveis
            orig = os.environ.pop(orig_key)
            if orig:
                os.environ[var] = orig
            else:
                os.environ.pop(var, None)
        elif _is_snap_path(os.environ.get(var, "")):
            entries = [p for p in os.environ[var].split(":") if p and not _is_snap_path(p)]
            if entries:
                os.environ[var] = ":".join(entries)
            else:
                os.environ.pop(var, None)

    # O carregador dinâmico só lê LD_LIBRARY_PATH na inicialização do processo,
    # então se houver caminhos do snap é preciso reiniciar o interpretador.
    ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    if _is_snap_path(ld_path) and not os.environ.get("OSCLINK_REEXEC"):
        entries = [p for p in ld_path.split(":") if p and not _is_snap_path(p)]
        if entries:
            os.environ["LD_LIBRARY_PATH"] = ":".join(entries)
        else:
            os.environ.pop("LD_LIBRARY_PATH", None)
        os.environ["OSCLINK_REEXEC"] = "1"
        os.execv(sys.executable, [sys.executable] + sys.argv)
