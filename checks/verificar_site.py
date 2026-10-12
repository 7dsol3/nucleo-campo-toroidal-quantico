"""QA do portal e das simulações servidas por HTTP, sem alterar os artefatos.

Teste local: --diretorio PASTA preparada por preparar_pages.py.
Teste do deploy: --url https://7dsol3.github.io/nucleo-campo-toroidal-quantico/
O servidor local usa o mesmo subdiretório do GitHub Pages para detectar links
que só funcionariam na raiz de um domínio. Nenhum ensaio físico é executado.
"""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
from urllib.parse import unquote, urljoin, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "nucleo_integral_v2"))
from browser_runtime import launch_browser

PREFIX = "/nucleo-campo-toroidal-quantico/"


class SubpathHandler(SimpleHTTPRequestHandler):
    """Expose a staging directory only underneath the repository path."""

    def translate_path(self, path):
        root = Path(self.directory).resolve()
        requested = unquote(urlsplit(path).path)
        if not requested.startswith(PREFIX):
            return str(root / "__outside_repository__")
        candidate = (root / requested[len(PREFIX):]).resolve()
        if not candidate.is_relative_to(root):
            return str(root / "__outside_repository__")
        return str(candidate)

    def log_message(self, *_args):
        pass


def exercise(base_url, checks):
    def check(name, condition, **evidence):
        checks.append({"name": name, "passed": bool(condition), **evidence})
        if not condition:
            raise AssertionError(name)

    base = urlsplit(base_url)
    failures, errors = [], []
    with sync_playwright() as playwright:
        browser = launch_browser(
            playwright,
            headless=True,
            args=["--enable-unsafe-swiftshader", "--use-angle=swiftshader"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 1050},
            device_scale_factor=1,
            accept_downloads=True,
        )
        page = context.new_page()
        page.set_default_timeout(30000)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("requestfailed", lambda request: failures.append({
            "url": request.url, "failure": request.failure,
        }))
        page.on("response", lambda response: failures.append({
            "url": response.url, "status": response.status,
        }) if response.status >= 400 else None)

        def visit(relative):
            response = page.goto(urljoin(base_url, relative), wait_until="load")
            check("http_" + (relative or "portal"), response and response.status == 200)

        def mobile(name):
            for width in (390, 768):
                page.set_viewport_size({"width": width, "height": 900})
                check(name + "_layout_" + str(width), page.evaluate(
                    "document.documentElement.scrollWidth <= innerWidth"
                ))
            page.set_viewport_size({"width": 1440, "height": 1050})

        visit("")
        check("portal_heading", page.locator("h1").count() == 1)
        check("portal_preview_loaded", page.locator("main img").evaluate(
            "image => image.complete && image.naturalWidth > 0"
        ))
        hrefs = page.locator("a[href]").evaluate_all(
            "links => links.map(link => link.getAttribute('href'))"
        )
        for target in ("nucleo_integral_v2/index.html", "nucleo_toroidal/index.html"):
            check("portal_link_" + target, target in hrefs)
        local_links = sorted({href for href in hrefs if href and not href.startswith("#")
                              and not urlsplit(href).scheme and not href.startswith("//")})
        check("portal_pdf_zip_links", any(href.endswith(".pdf") for href in local_links)
              and sum(href.endswith(".zip") for href in local_links) >= 2)
        for href in local_links:
            resolved = urlsplit(urljoin(base_url, href))
            check("portal_relative_" + href, not href.startswith("/")
                  and (resolved.scheme, resolved.netloc) == (base.scheme, base.netloc)
                  and resolved.path.startswith(base.path))
            response = context.request.head(urljoin(base_url, href))
            check("portal_target_" + href, response.status == 200, status=response.status)
        mobile("portal")

        visit("nucleo_integral_v2/index.html")
        page.wait_for_function("window.integralLab && integralLab.result && integralLab.renderer")
        check("v2_cad_loaded", page.evaluate("integralLab.renderer.parts.length") >= 160)
        check("v2_webgl", page.evaluate(
            "!!integralLab.renderer.gl && integralLab.renderer.gl.getError() === 0"
        ))
        page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        opaque_pixels = page.evaluate("""() => {
            const gl = integralLab.renderer.gl;
            const pixels = new Uint8Array(gl.drawingBufferWidth * gl.drawingBufferHeight * 4);
            gl.readPixels(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight,
                          gl.RGBA, gl.UNSIGNED_BYTE, pixels);
            let count = 0;
            for (let i = 3; i < pixels.length; i += 4) if (pixels[i] > 200) count++;
            return count;
        }""")
        check("v2_draws_pixels", opaque_pixels > 5000, opaque_pixels=opaque_pixels)
        check("v2_power_balance", abs(page.evaluate(
            "integralLab.result.power.balance_residual_w"
        )) < 1e-10)
        check("v2_default_receiver_power", page.evaluate(
            "integralLab.result.power.receiver_load_w"
        ) > 0)
        page.locator("#explode").click()
        check("v2_exploded_view", page.evaluate("integralLab.renderer.exploded"))
        page.locator("#explode").click()
        page.locator("#phase").fill("180")
        page.locator("#phase").dispatch_event("input")
        check("v2_phase_control", page.evaluate("integralLab.centerField.rms_norm_t") < 1e-9)
        page.locator("#reset").click()
        page.locator("#receiverEnabled").uncheck()
        check("v2_open_receiver", page.evaluate("integralLab.result.power.receiver_load_w") == 0)
        page.locator("#receiverEnabled").check()
        page.locator('[data-tab="tests"]').click()
        with page.expect_download() as download:
            page.locator("#template").click()
        template = Path(download.value.path()).read_text(encoding="utf-8-sig")
        check("v2_empty_measurement_template", len(template.splitlines()) == 1
              and "frequency_hz" in template)
        with page.expect_download() as download:
            page.locator("#export").click()
        scenario = json.loads(Path(download.value.path()).read_text(encoding="utf-8-sig"))
        check("v2_export_scenario", scenario["input"]["frequency_hz"] == 1400)
        page.locator('[data-tab="assembly"]').click()
        for selector in ("#voltageLower", "#voltageUpper"):
            page.locator(selector).fill("0")
            page.locator(selector).dispatch_event("input")
        check("v2_zero_drive", abs(page.evaluate("integralLab.result.power.source_total_w")) < 1e-12)
        page.locator("#reset").click()
        mobile("v2")

        visit("nucleo_toroidal/index.html")
        page.wait_for_function("window.lab && lab.circuit().I > 0")
        colors = page.locator("#model").evaluate("""canvas => {
            const data = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
            const colors = new Set();
            for (let i = 0; i < data.length; i += 16)
                colors.add(data[i] + ',' + data[i + 1] + ',' + data[i + 2]);
            return colors.size;
        }""")
        check("v1_canvas_draws_geometry", colors > 100, sampled_colors=colors)
        initial = page.evaluate("lab.circuit().I")
        page.locator("#explode").click()
        check("v1_exploded_view", page.evaluate("lab.state.explode"))
        page.locator("#explode").click()
        page.locator('[data-tab="sweep"]').click()
        page.locator("#resonance").click()
        check("v1_tune_resonance", page.evaluate("lab.circuit().I") > initial)
        page.locator("#voltage").fill("0")
        page.locator("#voltage").dispatch_event("input")
        check("v1_zero_drive", page.evaluate("lab.circuit().I") == 0)
        page.locator("#reset").click()
        with page.expect_download() as download:
            page.locator("#export").click()
        csv = Path(download.value.path()).read_text(encoding="utf-8-sig")
        check("v1_export_prediction", len(csv.splitlines()) == 492
              and csv.startswith("frequency_hz;"))
        page.locator('[data-tab="model"]').click()
        mobile("v1")
        check("no_javascript_errors", not errors, errors=errors)
        check("no_failed_assets", not failures, failures=failures)
        browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="URL raiz do portal publicado, incluindo subdiretório")
    source.add_argument("--diretorio", type=Path, help="Diretório de staging preparado para Pages")
    parser.add_argument("--output", type=Path, help="Relatório JSON; prefira caminho fora do repositório")
    args = parser.parse_args()
    server = None
    checks = []
    result = {"scope": "Portal HTTP e interação das simulações; nenhum ensaio físico.", "checks": checks}
    try:
        if args.diretorio:
            directory = args.diretorio.resolve()
            if not (directory / "index.html").is_file():
                raise ValueError("O staging precisa conter index.html na raiz")
            server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SubpathHandler, directory=str(directory)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_port}{PREFIX}"
        else:
            base_url = args.url.rstrip("/") + "/"
            parsed = urlsplit(base_url)
            if parsed.scheme not in ("https", "http") or not parsed.netloc or parsed.query or parsed.fragment:
                raise ValueError("Use uma URL HTTP(S) raiz, sem query ou fragmento")
        result["url"] = base_url
        exercise(base_url, checks)
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
    finally:
        if server:
            server.shutdown()
            server.server_close()
        result["all_passed"] = bool(checks) and all(check["passed"] for check in checks) and "error" not in result
        result["check_count"] = len(checks)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({key: result[key] for key in ("all_passed", "check_count", "error") if key in result}))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
