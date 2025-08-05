import shutil
import subprocess
import typing as t

from .pyproject_config import PyProjectConfig
from .sprinkles import Sprinkles


def strip_front_slash(path: str) -> str:
    if path.startswith("/"):
        return path[1:]
    return path


def update_vite_apps(
    pyproject_config: PyProjectConfig,
    vite_apps_found: t.List[t.Dict[str, t.Any]],
) -> None:
    updater(
        pyproject_config,
        vite_apps_found,
    )


def pack_vite_apps(
    pyproject_config: PyProjectConfig,
    vite_apps_found: t.List[t.Dict[str, t.Any]],
    mode: str = "production",
) -> None:
    packer(pyproject_config, vite_apps_found, mode=mode)


def transport_vite_apps(
    pyproject_config: PyProjectConfig,
    vite_apps_found: t.List[t.Dict[str, t.Any]],
    static_url_path: str = "/--vite--",
) -> None:
    transporter(pyproject_config, vite_apps_found, static_url_path)


def updater(
    pyproject_config: PyProjectConfig,
    vite_apps_found: t.List[t.Dict[str, t.Any]],
) -> None:
    for app in vite_apps_found:
        va_path = pyproject_config.cwd / app.get("vite_app", "")
        va_node_modules = va_path / "node_modules"
        va_dist = va_path / "dist"

        print(
            f"{Sprinkles.OKCYAN}⚙️ Updating npm for {app.get('vite_app', '')} ...{Sprinkles.END}"
        )

        if va_dist.exists() and va_dist.is_dir():
            shutil.rmtree(va_dist)

        if not va_node_modules.exists():
            subprocess.run([pyproject_config.npm_exec, "install"], cwd=va_path)

        subprocess.run([pyproject_config.npm_exec, "update"], cwd=va_path)

        print(f"{Sprinkles.OKGREEN}⚙️ {app.get('vite_app', '')} updated!{Sprinkles.END}")


def packer(
    pyproject_config: PyProjectConfig,
    vite_apps_found: t.List[t.Dict[str, t.Any]],
    mode: str = "production",
) -> None:
    for app in vite_apps_found:
        va_path = pyproject_config.cwd / app.get("vite_app", "")
        va_node_modules = va_path / "node_modules"
        va_dist = va_path / "dist"

        print(
            f"{Sprinkles.OKCYAN}📦 Packing {app.get('vite_app', '')} with Vite in {mode} mode ...{Sprinkles.END}"
        )

        if va_dist.exists() and va_dist.is_dir():
            shutil.rmtree(va_dist)

        if not va_node_modules.exists():
            subprocess.run([pyproject_config.npm_exec, "install"], cwd=va_path)

        subprocess.run(
            [pyproject_config.npx_exec, "vite", "build", "--mode", mode],
            cwd=va_path,
        )

        print(f"{Sprinkles.OKGREEN}📦 {app.get('vite_app', '')} packed!{Sprinkles.END}")


def transporter(
    pyproject_config: PyProjectConfig,
    vite_apps_found: t.List[t.Dict[str, t.Any]],
    static_url_path: str = "/--vite--",
) -> None:
    vt_dir = pyproject_config.cwd / pyproject_config.serve_app / "vite"

    if not vt_dir.exists():
        vt_dir.mkdir(parents=True)

    for app in vite_apps_found:
        va_path = pyproject_config.cwd / app.get("vite_app", "")
        va_dist = va_path / "dist"
        va_assets = va_dist / "assets"

        va_vt_path = vt_dir / app.get("serve_app_path", "")

        if not va_vt_path.exists():
            va_vt_path.mkdir(parents=True)
        else:
            for item in va_vt_path.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

        print(f"{Sprinkles.OKCYAN}🚚 Transporting to {va_vt_path} ...{Sprinkles.END}")

        if not va_dist.exists():
            print(f"{Sprinkles.FAIL}No dist found for {va_path.name}{Sprinkles.END}")
            continue

        for item in va_assets.iterdir():
            print(
                f"{Sprinkles.OKBLUE}Copying {item.name} to {va_vt_path}{Sprinkles.END}"
            )

            if item.suffix == ".js":
                with open(va_vt_path / item.name, "w") as f:
                    content = item.read_text()
                    f.write(
                        content.replace(
                            "assets/",
                            f"{strip_front_slash(static_url_path)}/{app.get('serve_app_path', '')}/",
                        )
                    )
            elif item.suffix == ".css":
                with open(va_vt_path / item.name, "w") as f:
                    content = item.read_text()
                    f.write(
                        content.replace(
                            "assets/",
                            f"{strip_front_slash(static_url_path)}/{app.get('serve_app_path', '')}/",
                        )
                    )
            else:
                shutil.copy(item, va_vt_path / item.name)

        print(f"{Sprinkles.OKGREEN}🚚 Destination reached!{Sprinkles.END}")
