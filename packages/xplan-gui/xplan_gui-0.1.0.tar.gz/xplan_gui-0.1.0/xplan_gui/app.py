import io
import json
import re
from copy import deepcopy
from uuid import uuid4

from nicegui import Client, app, ui
from osgeo import ogr
from xplan_tools.interface.gml import GMLRepository
from xplan_tools.model import model_factory, xplan60
from xplan_tools.model.base import BaseFeature

from xplan_gui.map import build_map
from xplan_gui.model_ui import model_ui_schema

MODELS = [
    model_factory(model, "60").get_name()
    for model in dir(xplan60)
    if re.match("^(SO|.P).*$", model)
    and getattr(model_factory(model, "60"), "model_fields", {}).get("id", None)
    and not model_factory(model, "60").__subclasses__()
]


def start_validation(final_obj: dict, model: BaseFeature, validation_log: ui.log):
    """
    Validates a feature object

    Args:
    final_obj (dict): The feature object to be validated
    model (BaseFeature): The model against which the object is validated.
    vaidation_log (ui.log): The log object in which validation and error messages are displayed.
    """
    clean_obj = deepcopy(final_obj)
    for k, v in clean_obj.items():
        if not v:
            clean_obj[k] = None
        elif isinstance(v, dict):
            filtered = list(filter(None, v.values()))
            if not filtered:
                clean_obj[k] = None
            else:
                for item in filtered:
                    if isinstance(item, dict):
                        if not list(filter(None, item.values())):
                            clean_obj[k] = None
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    if not list(filter(None, item.values())):
                        clean_obj[k] = None
    # clean_obj = {}
    # for k, v in final_obj.items():
    #     if app.storage.tab["switch"].get(k, None):
    #         clean_obj[k] = v
    try:
        app.storage.tab["collection"].update(
            {clean_obj["id"]: model.model_validate(clean_obj)}
        )
        validation_log.clear(), validation_log.push("all clear")
    except Exception as e:
        validation_log.clear(), validation_log.push(e)


def build_row(k, v, bind_obj):
    """
    Builds a UI row with label, optional info tooltip, and nullable switch-control.
    
    Args:
    k (str): The field name/key
    v (dict): Field metadata with keys
    bind_obj (dict): Dictionary bound to UI that holds current field values
    """
    switch = None
    with ui.row():
        ui.label(k)
        if v["description"]:
            ui.icon("o_info", size="xs").tooltip(v["description"])
    with ui.row():
        if v["nullable"] and k != "id":
            switch = ui.switch(value=True if bind_obj.get(k, None) else False)
    with ui.row():
        with ui.column().classes("w-full") as col:
            if v["nullable"]:
                col.bind_visibility_from(switch, "value")
    return col


def build_field(k, v, bind_obj):
    """
    Build and render a form input field based on its metadata and bind it to an object.
    Args:
        k (str): string
        v (dict[str, Any]): dictionary
        bind_obj (dict): dictionary

    """
    match v["type"]["name"]:
        case "str" | "reference":
            if k == "id":
                ui.label(app.storage.tab["id"]).bind_text_to(bind_obj, k)
            else:
                ui.textarea(
                    "Text",
                    validation=None
                    if v["nullable"]
                    else {"Pflichtfeld": lambda value: value},
                ).bind_value(
                    bind_obj, k, forward=lambda x: None if not x else x
                ).classes("w-full p-5").props("clearable autogrow")
        case "int":
            ui.number(
                "Ganzzahl",
                step=1,
                precision=0,
                format="%i",
                validation=None
                if v["nullable"]
                else {"Pflichtfeld": lambda value: value},
            ).bind_value(
                bind_obj,
                k,
                backward=lambda x: None if not x else x,
            ).classes("w-full p-5")
        case "float":
            ui.number(
                "Dezimalzahl",
                validation=None
                if v["nullable"]
                else {"Pflichtfeld": lambda value: value},
            ).bind_value(
                bind_obj,
                k,
                backward=lambda x: None if not x else x,
            ).classes("w-full p-5")
        case "date":
            with (
                ui.input(
                    "Datum",
                    validation=None
                    if v["nullable"]
                    else {"Pflichtfeld": lambda value: value},
                )
                .bind_value(
                    bind_obj,
                    k,
                    backward=lambda x: None if not x else x,
                )
                .classes("w-full p-5") as date
            ):
                with date.add_slot("append"):
                    ui.icon("edit_calendar").on("click", lambda: menu.open()).classes(
                        "cursor-pointer"
                    )
                with ui.menu() as menu:
                    ui.date().bind_value(date)
        case "enum":
            ui.select(
                v["type"]["options"],
                multiple=v["list"],
                validation=None
                if v["nullable"]
                else {"Pflichtfeld": lambda value: value},
            ).bind_value(
                bind_obj,
                k,
                backward=lambda x: None if not x else x,
            ).classes("w-full p-5")
        case "bool":
            ui.checkbox().bind_value(bind_obj, k)
        case "Url":
            ui.input(
                "URL",
                validation={
                    "Keine URL": lambda value: "://" in value if value else True,
                }
                if v["nullable"]
                else {
                    "Pflichtfeld": lambda value: value,
                    "Keine URL": lambda value: "://" in value if value else True,
                },
            ).bind_value(bind_obj, k, backward=lambda x: None if not x else x)
        # case "reference":
        #     ui.select(
        #         {None: "kein Objekt vorhanden"}
        #         | {
        #             id: f"{obj.get_name()} {id}"
        #             for id, obj in app.storage.tab["collection"].items()
        #         },
        #         multiple=v["list"],
        #         value=None,
        #         validation=None
        #         if v["nullable"]
        #         else {"Pflichtfeld": lambda value: value},
        #     ).bind_value(bind_obj, k).classes("w-full p-5")
        case _:
            ui.label("nicht unterstützter Typ")


@ui.refreshable
def sub_form(schema: dict, bind_obj: list):
    """
    Render a dynamic sub-form for a list of items
    Args:
        schema (dict): schema definition dict
        bind_obj (list[dict]): list of dictionary
    """
    # with ui.row().classes("w-full"):
    #     ui.button(
    #         icon="add",
    #         on_click=lambda: (
    #             bind_obj.append({}),
    #             sub_form.refresh(),
    #         ),
    #     ).classes("w-full")
    ui.button(
        icon="add",
        on_click=lambda: (
            bind_obj.append({}),
            sub_form.refresh(),
        ),
    )
    for item in bind_obj:
        index = bind_obj.index(item)
        with ui.card().classes("w-full"):
            ui.label(schema["name"])
            build_form(schema, item)
            with ui.row():
                ui.button(
                    on_click=lambda: (
                        bind_obj.pop(index),
                        sub_form.refresh(),
                    ),
                    icon="delete",
                )


@ui.refreshable
def choice_form(schema: list, bind_obj: list):
    """
    Render a dynamic sub-form allowing to choose form types.
    Args:
        schema (list[dict]): List of schema definitions
        bind_obj (list[dict]): list of dictionary
    """
    with ui.row():
        sel = ui.select({schema.index(option): option["name"] for option in schema})
        ui.button(
            icon="add",
            on_click=lambda: (
                bind_obj.append({"schema": sel.value}),
                choice_form.refresh(),
            ),
        )
    with ui.list():
        for item in bind_obj:
            index = bind_obj.index(item)
            with ui.item():
                with ui.card().classes("w-full p-5"):
                    ui.label(schema[item["schema"]]["name"])
                    build_form(
                        schema[item["schema"]],
                        item,
                    )
                ui.button(
                    on_click=lambda: (
                        bind_obj.pop(index),
                        choice_form.refresh(),
                    ),
                    icon="delete",
                )


@ui.refreshable
def build_form(schema: dict, bind_obj: dict):
    """
    Render a UI form based on the provided schema and bind it to an object.
     Args:
        schema (dict): schema definition
        bind_obj (dict): dictionary  
    """
    with ui.grid(columns="1fr 60px 3fr").classes("w-full"):
        for k, v in schema["fields"].items():
            if k in [
                "raeumlicherGeltungsbereich",
                "geltungsbereich",
                "position",
                "uom",
                "id",
            ]:
                continue
            col = build_row(k, v, bind_obj)
            with col:
                match v["type"]["name"]:
                    case "object":
                        name = str(k)
                        bind_obj.setdefault(k, [{}] if v["list"] else {})
                        if v["list"]:
                            sub_form(v["type"]["options"], bind_obj[name])
                        else:
                            with ui.card():
                                ui.label(v["type"]["options"]["name"])
                                build_form(v["type"]["options"], bind_obj[k])
                    case "choice":
                        bind_obj.setdefault(k, [] if v["list"] else {})
                        name = str(k)
                        if v["list"]:
                            with ui.row():
                                choice_form(v["type"]["options"], bind_obj[name])
                        # else:
                        #     with ui.card():
                        #         build_form(v["type"]["options"], bind_obj[k])
                    case _:
                        build_field(k, v, bind_obj)


def parse_geometry(fc: dict):
    """
    Parse a geometry from a dictionary
    Args:
        fc (dict): A dictionary containing a geometry key
    """
    collection = {
        "type": "GeometryCollection",
        "geometries": [feature["geometry"] for feature in fc["features"]],
    }
    if len(collection["geometries"]) > 1:
        ui.notify("zu viele Geometrien")
    else:
        geom = ogr.CreateGeometryFromJson(json.dumps(collection["geometries"][0]))
        app.storage.client["obj"][app.storage.tab["model"].get_geom_field()] = (
            f"SRID=4326;{geom.ExportToWkt()}"
        )
        geom = None


def update_form(attrs_area):
    """
    Refresh the current form by clearing and rebuilding it based on the active model.
    Args:
        attrs_area: A NiceGUI UI container (e.g., a row or column) where the form is rendered.
    """
    app.storage.tab["obj"].clear()
    attrs_area.clear()
    with attrs_area:
        ui.label().bind_text_from(
            app.storage.tab,
            "model",
            backward=lambda model: model.get_name(),
        ).classes("text-h5")
        build_form(model_ui_schema(app.storage.tab["model"]), app.storage.client["obj"])


@ui.refreshable
def collection_list():
    """
    Display a grid of links representing items in the current collection.
    Args:
        None
    """
    with ui.grid(columns=2):
        for k, v in app.storage.tab["collection"].items():
            ui.link(k, target=f"/features/{k}")
            ui.label(v.get_name())


@ui.page("/")
async def index(client: Client):
    """
    Render the main application index page
    Args:
    client (Client): A NiceGUI client instance; this function awaits `client.connected()`.
  
    """
    await client.connected()
    with ui.header():
        ui.button(
            icon="home",
            on_click=lambda: ui.navigate.to("/"),
        )
    with ui.row():
        ui.select(
            options=MODELS,
            value="BP_Plan",
            label="Objektklasse auswählen",
            with_input=True,
        ).bind_value_to(
            app.storage.tab, "model", forward=lambda x: model_factory(x, "6.0")
        )
        # app.storage.tab["obj"] = {}
        app.storage.tab.setdefault("collection", {})
        ui.button(
            "Neues Objekt anlegen",
            on_click=lambda: ui.navigate.to(f"/features/{uuid4()}"),
        )
    with ui.row():

        def handle_upload(e):
            file_buffer = io.BytesIO(e.content.read())
            repo = GMLRepository(file_buffer, "6.0")
            app.storage.tab["collection"] = repo.get_all().features
            collection_list.refresh()

        ui.upload(on_upload=handle_upload).props("accept=.gml")
    with ui.row():
        collection_list()


@ui.page("/features/{uuid}", response_timeout=10)
async def feature(uuid: str, client: Client):
    """
    Render the feature editing page for a given UUID.
    Args:
        uuid (str): Unique identifier for the feature to be edited.
        client (Client): NiceGUI client used to manage real-time UI interaction.
    """
    await client.connected()
    ui.on("drawing", lambda e: parse_geometry(e.args))
    app.storage.tab["id"] = uuid
    app.storage.tab.setdefault("collection", {})
    if obj := app.storage.tab["collection"].get(uuid, None):
        app.storage.client["obj"] = obj.model_dump(mode="json", exclude_none=True)
        app.storage.client["feature"] = obj.model_dump_jsonfg()
        app.storage.tab["model"] = obj.__class__
    else:
        app.storage.client["obj"] = {}
    if not app.storage.tab.get("model", None):
        ui.navigate.to("/")
    with ui.header():
        ui.button(
            icon="home",
            on_click=lambda: ui.navigate.to("/"),
        )
        ui.button(
            icon="save",
            on_click=lambda: start_validation(
                app.storage.client["obj"],
                app.storage.tab["model"],
                validation_log,
            ),
        )
        ui.button(
            icon="delete",
            on_click=lambda: update_form(attr_area),
        )
    with ui.grid(columns=2).classes("w-full gap-10"):
        with ui.card().classes("w-full"):
            with ui.column() as attr_area:
                # if not app.storage.tab.get("model", None):
                #     ui.navigate.to("/")
                # else:
                ui.label().bind_text_from(
                    app.storage.tab,
                    "model",
                    backward=lambda model: model.get_name(),
                ).classes("text-h5")
                build_form(
                    model_ui_schema(app.storage.tab["model"]),
                    app.storage.client["obj"],
                )
        with ui.column().classes("w-full"):
            with ui.row().classes("w-full"):
                build_map(
                    height="1000px", feature=app.storage.client.get("feature", None)
                ).classes("w-full")
            with ui.grid(columns=2).classes("w-full"):
                with ui.column().classes("w-full"):
                    obj_log = ui.log()
                    ui.button(
                        "show model",
                        on_click=lambda: (
                            obj_log.clear(),
                            obj_log.push(
                                json.dumps(app.storage.client["obj"], indent=2)
                            ),
                        ),
                    )
                    ui.button(
                        "show collection",
                        on_click=lambda: (
                            obj_log.clear(),
                            obj_log.push(
                                json.dumps(
                                    {
                                        k: v.model_dump(mode="json", exclude_none=True)
                                        for k, v in app.storage.tab.get(
                                            "collection", {}
                                        ).items()
                                    },
                                    indent=2,
                                )
                            ),
                        ),
                    )
                with ui.column().classes("w-full"):
                    validation_log = ui.log()
                    ui.button(
                        "validate",
                        on_click=lambda: start_validation(
                            app.storage.client["obj"],
                            app.storage.tab["model"],
                            validation_log,
                        ),
                    )


ui.run(
    port=8888,
    dark=False,
    reload=True,
    uvicorn_logging_level="info",
    binding_refresh_interval=1,
    reconnect_timeout=10,
)
