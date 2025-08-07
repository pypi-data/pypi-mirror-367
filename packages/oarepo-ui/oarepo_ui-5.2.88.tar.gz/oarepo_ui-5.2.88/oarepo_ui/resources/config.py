import inspect
from pathlib import Path

import marshmallow as ma
from flask import current_app
from flask_resources import ResourceConfig
from flask_resources import (
    resource_requestctx,
)
from invenio_base.utils import obj_or_import_string
from invenio_pidstore.errors import (
    PIDDeletedError,
    PIDDoesNotExistError,
    PIDUnregistered,
)
from invenio_rdm_records.services.errors import RecordDeletedException
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services import Link, pagination_links
from invenio_records_resources.services.errors import (
    FileKeyNotFoundError,
    PermissionDeniedError,
)
from invenio_search_ui.searchconfig import FacetsConfig, SearchAppConfig, SortConfig
from oarepo_runtime.services.custom_fields import CustomFields, InlinedCustomFields

from flask_resources.parsers import MultiDictSchema
from marshmallow import fields, post_load, validate

from oarepo_ui.resources.links import UIRecordLink


def _(x):
    """Identity function used to trigger string extraction."""
    return x


class SearchRequestArgsSchema(MultiDictSchema):
    """Request URL query string arguments."""

    q = fields.String()
    suggest = fields.String()
    sort = fields.String()
    page = fields.Integer()
    size = fields.Integer()
    layout = fields.String(validate=validate.OneOf(["grid", "list"]))

    @post_load(pass_original=True)
    def facets(self, data, original_data=None, **kwargs):
        """Extract facet filters from 'f=facetName:facetValue' style arguments."""

        for value in original_data.getlist("f"):
            if ":" in value:
                key, val = value.split(":", 1)
                data.setdefault("facets", {}).setdefault(key, []).append(val)

        return data


class UIResourceConfig(ResourceConfig):
    components = None
    template_folder = None

    def get_template_folder(self):
        if not self.template_folder:
            return None

        tf = Path(self.template_folder)
        if not tf.is_absolute():
            tf = (
                Path(inspect.getfile(type(self)))
                .parent.absolute()
                .joinpath(tf)
                .absolute()
            )
        return str(tf)

    response_handlers = {"text/html": None, "application/json": None}
    default_accept_mimetype = "text/html"

    # Request parsing
    request_read_args = {}
    request_view_args = {}


class FormConfigResourceConfig(ResourceConfig):
    application_id = "Default"

    def form_config(self, **kwargs):
        """Get the react form configuration."""

        return dict(
            **kwargs,
        )

    request_view_args = {}
    components = None


class TemplatePageUIResourceConfig(UIResourceConfig):
    pages = {}
    """
       Templates used for rendering the UI. 
       The key in the dictionary is URL path (relative to url_prefix), 
       value is a jinjax macro that renders the UI
   """


class RecordsUIResourceConfig(UIResourceConfig):
    routes = {
        "search": "",
        "create": "/_new",
        "detail": "/<pid_value>",
        "edit": "/<pid_value>/edit",
        "export": "/<pid_value>/export/<export_format>",
        "export_preview": "/<pid_value>/preview/export/<export_format>",
        "preview": "/<pid_value>/preview",
        "published_file_preview": "/<pid_value>/files/<path:filepath>/preview",
        "draft_file_preview": "/<pid_value>/preview/files/<path:filepath>/preview",
    }
    config_url_prefix = "/configs"
    config_routes = {
        "form_config": "form",
    }
    request_view_args = {"pid_value": ma.fields.Str()}
    request_file_view_args = {**request_view_args, "filepath": ma.fields.Str()}
    request_export_args = {"export_format": ma.fields.Str()}
    request_search_args = SearchRequestArgsSchema
    request_create_args = {"community": ma.fields.Str()}
    request_embed_args = {"embed": ma.fields.Str()}
    request_form_config_view_args = {}

    app_contexts = None
    ui_serializer = None
    ui_serializer_class = None

    api_service = None
    """Name of the API service as registered inside the service registry"""

    application_id = "Default"
    """Namespace of the React app components related to this resource."""

    templates = {
        "detail": None,
        "search": None,
        "edit": None,
        "create": None,
        "preview": None,
    }
    """Templates used for rendering the UI. It is a name of a jinjax macro that renders the UI"""

    empty_record = {}

    error_handlers = {
        PIDDeletedError: "tombstone",
        RecordDeletedException: "tombstone",
        PIDDoesNotExistError: "not_found",
        PIDUnregistered: "not_found",
        KeyError: "not_found",
        FileKeyNotFoundError: "not_found",
        PermissionDeniedError: "permission_denied",
    }

    @property
    def default_components(self):
        service = current_service_registry.get(self.api_service)
        schema = getattr(service.record_cls, "schema", None)
        component = getattr(self, "search_component", None)
        if schema and component:
            return {schema.value: component}
        else:
            return {}

    ui_links_item = {
        "self": UIRecordLink("{+ui}{+url_prefix}/{id}"),
        "edit": UIRecordLink("{+ui}{+url_prefix}/{id}/edit"),
        "search": UIRecordLink("{+ui}{+url_prefix}/"),
    }

    @property
    def ui_links_search(self):
        return {
            **pagination_links("{+ui}{+url_prefix}{?args*}"),
            "create": Link("{+ui}{+url_prefix}/_new"),
        }

    @property
    def ui_serializer(self):
        return obj_or_import_string(self.ui_serializer_class)()

    def search_available_facets(self, api_config, identity):
        classes = api_config.search.params_interpreters_cls
        grouped_facets_param_class = next(
            (
                cls
                for cls in classes
                if getattr(cls, "__name__", None) == "GroupedFacetsParam"
            ),
            None,
        )
        if not grouped_facets_param_class:
            return api_config.search.facets
        grouped_facets_param_instance = grouped_facets_param_class(api_config.search)

        return grouped_facets_param_instance.identity_facets(identity)

    def search_available_sort_options(self, api_config, identity):
        return api_config.search.sort_options

    def search_active_facets(self, api_config, identity):
        """Return list of active facets that will be displayed by search app.
        By default, all facets are active but a repository can, for performance reasons,
        display only a subset of facets.
        """
        return list(self.search_available_facets(api_config, identity).keys())

    def additional_filter_labels(self):
        """
        Returns human-readable list of filters that are currently applied in the URL.
        Sometimes those are not available in the response from the search API.
        """
        translated_params = {}
        facets = {}

        for model in current_app.config.get("GLOBAL_SEARCH_MODELS", []):
            service_config_cls = obj_or_import_string(model["service_config"])
            search_options = service_config_cls.search
            facets = {**facets, **search_options.facets}

        for k, v in resource_requestctx.args.get("facets", {}).items():
            facet = facets.get(k)
            if not facet:
                continue

            translated_params.setdefault(k, {})
            translated_params[k]["label"] = facet._label

            value_labels_attr = getattr(facet, "_value_labels", None)
            if not value_labels_attr:
                translated_params[k]["buckets"] = [{"key": key} for key in v]
                continue

            if callable(value_labels_attr):
                value_labels = value_labels_attr(v)
            elif isinstance(value_labels_attr, dict):
                value_labels = value_labels_attr
            else:
                value_labels = {}

            translated_params[k]["buckets"] = [
                {"key": key, "label": value_labels.get(key, key)} for key in v
            ]

        return translated_params

    def search_active_sort_options(self, api_config, identity):
        return list(api_config.search.sort_options.keys())

    def search_sort_config(
        self,
        available_options,
        selected_options=[],
        default_option=None,
        no_query_option=None,
    ):
        return SortConfig(
            available_options, selected_options, default_option, no_query_option
        )

    def search_facets_config(self, available_facets, selected_facets=[]):
        facets_config = {}
        for facet_key, facet in available_facets.items():
            facets_config[facet_key] = {
                "facet": facet,
                "ui": {
                    "field": facet._params.get("field", facet_key),
                },
            }

        return FacetsConfig(facets_config, selected_facets)

    def ignored_search_filters(self):
        """
        Return a list of search filters to ignore.

        Override this method downstream to specify which filters should be ignored.
        """
        return ["allversions"]

    def search_endpoint_url(self, identity, api_config, overrides={}, **kwargs):
        return f"/api{api_config.url_prefix}"

    def search_app_config(self, identity, api_config, overrides={}, **kwargs):
        opts = {
            "endpoint": self.search_endpoint_url(
                identity, api_config, overrides=overrides, **kwargs
            ),
            "headers": {"Accept": "application/vnd.inveniordm.v1+json"},
            "grid_view": False,
            "sort": self.search_sort_config(
                available_options=self.search_available_sort_options(
                    api_config, identity
                ),
                selected_options=self.search_active_sort_options(api_config, identity),
                default_option=api_config.search.sort_default,
                no_query_option=api_config.search.sort_default_no_query,
            ),
            "facets": self.search_facets_config(
                available_facets=self.search_available_facets(api_config, identity),
                selected_facets=self.search_active_facets(api_config, identity),
            ),
        }
        opts.update(kwargs)
        return SearchAppConfig.generate(opts, **overrides)

    def custom_fields(self, **kwargs):
        api_service = current_service_registry.get(self.api_service)
        # get the record class
        record_class = getattr(api_service, "record_cls", None) or getattr(
            api_service, "draft_cls", None
        )
        ui = []
        ret = {
            "ui": ui,
        }
        if not record_class:
            return ret
        # try to get custom fields from the record
        for fld_name, fld in sorted(inspect.getmembers(record_class)):
            if isinstance(fld, InlinedCustomFields):
                prefix = ""
            elif isinstance(fld, CustomFields):
                prefix = fld.key + "."
            else:
                continue

            ui_config = self._get_custom_fields_ui_config(fld.config_key, **kwargs)
            if not ui_config:
                continue

            for section in ui_config:
                ui.append(
                    {
                        **section,
                        "fields": [
                            {
                                **field,
                                "field": prefix + field["field"],
                            }
                            for field in section.get("fields", [])
                        ],
                    }
                )
        return ret

    def _get_custom_fields_ui_config(self, key, **kwargs):
        return current_app.config.get(f"{key}_UI", [])

    def form_config(self, identity=None, **kwargs):
        """Get the react form configuration."""

        return dict(
            overridableIdPrefix=f"{self.application_id.capitalize()}.Form",
            **kwargs,
        )
