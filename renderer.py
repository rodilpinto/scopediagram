from __future__ import annotations

from io import BytesIO
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

from schema import ScopeDiagram, Subprocess


WIDTH = 1600
HEIGHT = 900


class Palette:
    background = (255, 255, 255)
    title = (41, 52, 43)
    muted = (84, 98, 90)
    line = (196, 203, 197)
    header_green = (50, 106, 62)
    header_orange = (222, 136, 37)
    objective_fill = (252, 241, 221)
    regulators_fill = (244, 234, 210)
    resources_fill = (235, 242, 229)
    event_fill = (243, 245, 241)
    inputs_fill = (241, 247, 237)
    activities_fill = (255, 245, 230)
    outputs_fill = (244, 250, 240)
    lane_label_fill = (85, 128, 70)
    lane_label_text = (255, 255, 255)


def _load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


HEADER_FONT = _load_font(18, bold=True)
TITLE_FONT = _load_font(27, bold=True)
SECTION_FONT = _load_font(19, bold=True)
BODY_FONT = _load_font(17)
SMALL_FONT = _load_font(15, bold=True)


def _draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    *,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    line_spacing: int = 5,
    bullet: bool = False,
) -> None:
    left, top, right, bottom = box
    y = top
    width = max(120, right - left)
    chars_per_line = max(12, int(width / max(font.size * 0.58, 7)))

    for raw_line in (text.splitlines() if text else []):
        prefix = "• " if bullet else ""
        line = raw_line.strip() or ""
        wrapped = wrap(line, width=chars_per_line) if line else [""]
        for idx, part in enumerate(wrapped):
            current = f"{prefix}{part}" if bullet and idx == 0 else part
            draw.text((left, y), current, font=font, fill=fill)
            y += font.size + line_spacing
            if y > bottom:
                return


def _load_logo_image() -> Image.Image | None:
    candidate_paths = [
        Path("assets/logo-camara.png"),
        Path("assets/logo_camara.png"),
        Path("assets/camara_logo.png"),
        Path("assets/camara-dos-deputados.png"),
    ]
    for path in candidate_paths:
        if path.exists():
            return Image.open(path).convert("RGBA")
    return None


def _draw_header(image: Image.Image, draw: ImageDraw.ImageDraw, title: str) -> None:
    draw.rounded_rectangle((24, 18, 1576, 106), radius=18, fill=(249, 251, 248), outline=Palette.line, width=2)
    logo = _load_logo_image()
    if logo is not None:
        logo.thumbnail((180, 56))
        image.alpha_composite(logo, (42, 34))
    else:
        draw.rounded_rectangle((42, 34, 92, 84), radius=8, fill=Palette.header_green)
        draw.rectangle((96, 34, 126, 84), fill=Palette.header_orange)
        draw.text((138, 44), "Câmara dos Deputados", font=HEADER_FONT, fill=Palette.header_green)

    draw.text((138, 68), "Secretaria de Controle Interno", font=BODY_FONT, fill=Palette.muted)
    title_box = draw.textbbox((0, 0), title, font=TITLE_FONT)
    title_width = title_box[2] - title_box[0]
    draw.text((1544 - title_width, 46), title, font=TITLE_FONT, fill=Palette.title)


def _draw_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    fill: tuple[int, int, int],
    title: str,
    body: str,
    body_font: ImageFont.ImageFont = BODY_FONT,
) -> None:
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=Palette.line, width=2)
    left, top, right, bottom = box
    draw.text((left + 18, top + 12), title, font=SECTION_FONT, fill=Palette.muted)
    _draw_wrapped_text(
        draw,
        body or "N/A",
        (left + 18, top + 44, right - 18, bottom - 14),
        font=body_font,
        fill=Palette.title,
    )


def _draw_vertical_lane(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    fill: tuple[int, int, int],
    label: str,
    items: list[str],
) -> None:
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=Palette.line, width=2)
    label_box = (left + 10, top + 10, left + 80, bottom - 10)
    draw.rounded_rectangle(label_box, radius=12, fill=Palette.lane_label_fill)

    label_img = Image.new("RGBA", (bottom - top - 20, 70), (255, 255, 255, 0))
    label_draw = ImageDraw.Draw(label_img)
    text_bbox = label_draw.textbbox((0, 0), label, font=SMALL_FONT)
    label_draw.text(
        ((label_img.width - (text_bbox[2] - text_bbox[0])) / 2, (label_img.height - (text_bbox[3] - text_bbox[1])) / 2),
        label,
        font=SMALL_FONT,
        fill=Palette.lane_label_text,
    )
    rotated = label_img.rotate(90, expand=True)
    image.alpha_composite(rotated, (left + 10, top + int((bottom - top - rotated.height) / 2)))

    _draw_wrapped_text(
        draw,
        "\n".join(items or ["N/A"]),
        (left + 104, top + 18, right - 16, bottom - 16),
        font=BODY_FONT,
        fill=Palette.title,
        bullet=True,
    )


def _render_diagram(scope: ScopeDiagram, title: str, middle_label: str, middle_items: list[str], subprocess: Subprocess | None) -> bytes:
    image = Image.new("RGBA", (WIDTH, HEIGHT), Palette.background + (255,))
    draw = ImageDraw.Draw(image)
    _draw_header(image, draw, title)

    regulators = (
        subprocess.regulators if subprocess and subprocess.regulators else scope.global_elements.regulators if scope.global_elements else []
    )
    resources = (
        subprocess.resources if subprocess and subprocess.resources else scope.global_elements.resources if scope.global_elements else []
    )
    inputs = subprocess.inputs if subprocess else (scope.global_elements.inputs if scope.global_elements else [])
    outputs = subprocess.outputs if subprocess else (scope.global_elements.outputs if scope.global_elements else [])
    objective = subprocess.objective if subprocess and subprocess.objective else scope.process.objective
    start_event = subprocess.start_event if subprocess and subprocess.start_event else scope.process.start_event
    end_event = subprocess.end_event if subprocess and subprocess.end_event else scope.process.end_event

    _draw_panel(draw, (28, 126, 1572, 214), fill=Palette.objective_fill, title="OBJETIVO", body=objective)
    _draw_panel(draw, (28, 232, 1572, 364), fill=Palette.regulators_fill, title="REGULADORES", body="\n".join(regulators) or "N/A")
    _draw_vertical_lane(image, draw, (28, 384, 520, 742), fill=Palette.inputs_fill, label="ENTRADAS", items=inputs)
    _draw_vertical_lane(image, draw, (554, 384, 1046, 742), fill=Palette.activities_fill, label=middle_label, items=middle_items)
    _draw_vertical_lane(image, draw, (1080, 384, 1572, 742), fill=Palette.outputs_fill, label="SAÍDAS", items=outputs)
    _draw_panel(draw, (28, 760, 1572, 832), fill=Palette.resources_fill, title="RECURSOS DE SUPORTE", body="\n".join(resources) or "N/A", body_font=SMALL_FONT)
    _draw_panel(draw, (28, 846, 782, 888), fill=Palette.event_fill, title="EVENTO DE INÍCIO", body=start_event, body_font=SMALL_FONT)
    _draw_panel(draw, (818, 846, 1572, 888), fill=Palette.event_fill, title="EVENTO DE FIM", body=end_event, body_font=SMALL_FONT)

    output = BytesIO()
    image.convert("RGB").save(output, format="PNG")
    return output.getvalue()


def build_preview_images(scope: ScopeDiagram) -> list[tuple[str, bytes]]:
    previews = [
        (
            "Processo principal",
            _render_diagram(
                scope,
                f"Processo {scope.process.name}",
                "SUBPROCESSOS",
                [subprocess.name for subprocess in scope.subprocesses],
                None,
            ),
        )
    ]
    for subprocess in scope.subprocesses:
        previews.append(
            (
                f"Subprocesso: {subprocess.name}",
                _render_diagram(scope, subprocess.name, "ATIVIDADES", subprocess.activities, subprocess),
            )
        )
    return previews
