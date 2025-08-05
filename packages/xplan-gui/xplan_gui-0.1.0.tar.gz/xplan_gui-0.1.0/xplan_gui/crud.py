from urllib.parse import unquote

from nicegui import app, binding, ui
from pydantic import ValidationError
from xplan_gui.app import MODELS, build_form
from xplan_gui.model_ui import model_ui_schema
from xplan_tools.interface.db import DBRepository
from xplan_tools.model import model_factory

repo = DBRepository("postgresql://postgres:postgres@gv-srv-w00173:5434/postgres", "6.0")


class State:
    model = binding.BindableProperty()
    feature = binding.BindableProperty()

    def __init__(self):
        self.model = None
        self.feature = {}


def clean_obj(obj):
    """
    Recursively remove keys with None or empty string values

    Args:
        obj (dict): The dictionary to be cleaned.
    """    
    cleaned = {}
    for k, v in obj.items():
        if isinstance(v, dict):
            if x := clean_obj(v):
                cleaned[k] = x
        elif isinstance(v, list):
            clean_list = []
            for item in v:
                if isinstance(item, dict):
                    if x := clean_obj(item):
                        clean_list.append(x)
                elif v is not None and v != "":
                    clean_list.append(item)
            if clean_list:
                cleaned[k] = clean_list
        elif v is not None and v != "":
            cleaned[k] = v
    return cleaned


def add_form(content, geom):
    """
    Adds a form to the specified content layer and sets the geometry.
    
    Args:
    content (ui.page): The content layer to which the form is added.
    geom (str): The geometry
    """
    geom = f"SRID=25832;{unquote(geom).upper()}"
    print(geom)
    app.storage.client["state"].feature[
        app.storage.client["state"].model.get_geom_field()
    ] = geom
    with content:
        build_form(
            model_ui_schema(app.storage.client["state"].model),
            app.storage.client["state"].feature,
        )


def handle_save():
    """saves the current object"""
    obj = clean_obj(app.storage.client["obj"])
    try:
        app.storage.client["state"].model.model_validate(obj)
    except ValidationError as e:
        ui.notify(e)
        print(e)


@ui.page("/{id}")
def feature(id: str, geom: str = ""):
    """
    Shows the detailed view of a feature based on the ID transferred.

    Args:
    id (str): The unique identifier of the feature
    geom (str, optional): The geometry of the feature

    """
    app.storage.client["state"] = State()
    try:
        feature = repo.get(id)
        ft = feature.get_name()
        app.storage.client["state"].feature = feature.model_dump(
            mode="json", exclude_none=True
        )
    except ValueError:
        ft = None
        app.storage.client["state"].feature = {}
    with ui.header():
        sel = ui.select(
            options=MODELS,
            value=ft,
            label="Objektklasse",
            on_change=lambda x: (
                sel.disable(),
                add_form(content, geom),
            ),
            with_input=True,
        ).bind_value_to(
            app.storage.client["state"],
            "model",
            forward=lambda x: model_factory(x, "6.0") if x else None,
        )
        ui.button(
            icon="save",
            on_click=handle_save,
        )
        ui.button(icon="delete")
    with ui.row() as content:
        if ft:
            sel.disable()
            add_form(content, geom)


ui.run(port=8888, reconnect_timeout=10)
