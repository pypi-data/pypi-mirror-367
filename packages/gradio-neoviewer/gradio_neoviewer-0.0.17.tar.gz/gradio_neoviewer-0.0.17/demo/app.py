import json
import gradio as gr
from gradio_neoviewer import NeoViewer
from gradio.themes.utils.sizes import Size

with open("../../neo_front/theme/dark_theme.json") as file:
    dark_theme_params = json.loads(file.read())


radius_neo = Size(
    name="radius_neo",
    xxs="5px",
    xs="5px",
    sm="5px",
    md="10px",
    lg="10px",
    xl="10px",
    xxl="10px",
)

theme = gr.themes.Monochrome(
    font=[gr.themes.GoogleFont("Poppins")],
    font_mono=[gr.themes.GoogleFont("IBM Plex Mono")],
    radius_size=radius_neo,
    spacing_size="sm",
    text_size="md",
).set(**dark_theme_params)


def set_interface():
    print("Setting interface")
    view_with_ms = NeoViewer(
        value=[
            "./demo/data/mermaid_graph-2.html",
            "./demo/data/graphique_couts_annuels.png",
            "./demo/data/Le_Petit_Chaperon_Rouge.zouzou",
            "./demo/data/calculate_cosine.py",
            "./demo/data/Le_Petit_Chaperon_Rouge_Modifie.docx",
        ],
        elem_classes=["visualisation"],
        index_of_file_to_show=0,
        height=300,
        visible=True,
        ms_files=True,
    )

    view_without_ms = NeoViewer(
        value=[
            # "./demo/data/Le_Petit_Chaperon_Rouge_Modifie.docx",
            "./demo/data/mermaid_graph-2.html",
            "./demo/data/graphique_couts_annuels.png",
            "./demo/data/Le_Petit_Chaperon_Rouge.zouzou",
        ],
        elem_classes=["visualisation"],
        index_of_file_to_show=1,
        height=300,
        visible=True,
        ms_files=False,
    )
    empty_view1 = view_with_ms
    empty_view2 = view_without_ms
    return view_with_ms, view_without_ms, empty_view1, empty_view2


with gr.Blocks(theme=theme) as demo:
    with gr.Row():
        view_with_ms = NeoViewer(visible=False)
        view_without_ms = NeoViewer(visible=False)
        empty_view1 = NeoViewer(visible=False)
        empty_view2 = NeoViewer(visible=False)
    demo.load(
        set_interface,
        outputs=[view_with_ms, view_without_ms, empty_view1, empty_view2],
    ).then(
        fn=lambda: (
            NeoViewer(visible=False, value=None, elem_id="empty1"),
            NeoViewer(visible=False, value=[], elem_id="empty2"),
        ),
        outputs=[empty_view1, empty_view2],
    )

if __name__ == "__main__":
    demo.launch()
