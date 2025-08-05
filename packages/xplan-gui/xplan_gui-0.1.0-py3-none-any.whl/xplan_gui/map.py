import json

import folium
from nicegui import ui


def build_map(height: str, feature: dict | None):
    # see https://geoman.io/blog/using-geoman-with-folium
    m = folium.Map()
    m.fit_bounds([[47.3024876979, 5.98865807458], [54.983104153, 15.0169958839]])
    folium.GeoJson(
        "https://api.hamburg.de/datasets/v1/alkis_vereinfacht/collections/Flurstueck/items?bbox=10.0240%2C53.5460%2C10.0357%2C53.5506&limit=1000&f=json",
        style_function=lambda feature: {
            "color": "black",
            "weight": 1,
            "opacity": 0.5,
            "fillOpacity": 0,
        },
    ).add_to(m)
    m.render()

    m.get_root().header.add_child(
        folium.CssLink(
            "https://unpkg.com/@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css"
        )
    )
    m.get_root().header.add_child(
        folium.JavascriptLink(
            "https://unpkg.com/@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.min.js"
        )
    )
    m.get_root().height = height
    m.get_root().script.add_child(
        folium.Element(f"""
            {m.get_name()}.pm.addControls();
            const features = L.geoJSON().addTo({m.get_name()});
            {m.get_name()}.pm.setGlobalOptions(
                {{layerGroup: features}}
            );
            const feature = {json.dumps(feature)}
            if (feature) {{
                features.addData(feature);
                {m.get_name()}.fitBounds(features.getBounds())
            }};
            {m.get_name()}.on("pm:create", (e) => {{
                console.log(features.toGeoJSON());
                parent.emitEvent("drawing", features.toGeoJSON())
            }});
        """)
    )
    map = ui.html(
        m.get_root()._repr_html_()
    )  # see https://github.com/zauberzeug/nicegui/discussions/487#discussioncomment-5301656
    return map
