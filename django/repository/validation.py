from django.core.exceptions import ValidationError as DjangoValidationError
from jsonschema import FormatChecker, validate
from jsonschema.exceptions import ValidationError as SchemaValidationError

from repository.models import Package, PackageVersion

NAME_PATTERN = r"^[a-zA-Z0-9 -_]+$"
WORD_PATTERN = r"^[a-zA-Z0-9-_]+$"
CLASS_PATTERN = r"^[a-zA-Z]+$"
SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
VERSION_PATTERN = r"^[0-9]+\.[0-9]+\.[0-9]+$"
DLL_PATTERN = r"^[a-zA-Z0-9-_]+\.dll$"

name_schema = {
    "type": "string",
    "maxLength": Package._meta.get_field("name").max_length,
    "pattern": NAME_PATTERN,
}

author_schema = {
    "type": "string"
}

url_schema = {
    "type": "string",
    "maxLength": PackageVersion._meta.get_field("website_url").max_length,
    "format": "uri"
}

version_schema = {
    "type": "string",
    "maxLength": PackageVersion._meta.get_field("version_number").max_length,
    "pattern": VERSION_PATTERN,
}

description_schema = {
    "type": "string",
    "maxLength": PackageVersion._meta.get_field("description").max_length
}

dependency_schema = {
    "type": "object",
    "properties": {
        "MinVersion": {"type": "string"},
        "MaxVersion": {"type": "string"},
    }
}

dependencies_schema = {
    "type": "object",
    "additionalProperties": dependency_schema,
    "propertyNames": {
        "pattern": SLUG_PATTERN
    }
}

target_schema = {
    "type": "object",
    "properties": {
        "MinVersion": {"type": "string"},
        "MaxVersion": {"type": "string"},
    }
}

targets_schema = {
    "type": "object",
    "additionalProperties": target_schema,
    "propertyNames": {
        "pattern": SLUG_PATTERN
    }
}

content_types_schema = {
    "type": "integer"
}

artifacts_schema = {
    "type": "array",
    "items": {"type": "string"},
}

preload_assemblies_schema = {
    "type": "array",
    "items": {
        "type": "string",
        "pattern": DLL_PATTERN
    }
}

preload_class_schema = {
    "type": "string",
    "pattern": CLASS_PATTERN,
}

preload_assembly_schema = {
    "type": "string",
    "pattern": CLASS_PATTERN,
}

runtime_assemblies_schema = {
    "type": "array",
    "contains": {
        "type": "string",
        "pattern": DLL_PATTERN
    }
}

runtime_class_schema = {
    "type": "string",
    "pattern": CLASS_PATTERN,
}

runtime_assembly_schema = {
    "type": "string",
    "pattern": CLASS_PATTERN,
}

manifest_schema = {
    "type": "object",
    "properties": {
        "Name": name_schema,
        "Url": url_schema,
        "Version": version_schema,
        "Description": description_schema,
        "Dependencies": dependencies_schema,
        "Targets": targets_schema,
        "ContentTypes": content_types_schema,
        "Artifacts": artifacts_schema,
        "PreloadAssemblies": preload_assemblies_schema,
        "PreloadAssembly": preload_assembly_schema,
        "PreloadClass": preload_class_schema,
        "RuntimeAssemblies": runtime_assemblies_schema,
        "RuntimeAssembly": runtime_assembly_schema,
        "RuntimeClass": runtime_class_schema,
    },

    "required": [
        "Name", "Url", "Version",  "Description", "Targets", "ContentTypes"],

    "dependencies": {
        "PreloadClass": ["PreloadAssemblies", "PreloadAssembly"],
        "PreloadAssembly": ["PreloadAssemblies", "PreloadClass"],
        "RuntimeClass": ["RuntimeAssemblies", "RuntimeAssembly"],
        "RuntimeAssembly": ["RuntimeAssemblies", "RuntimeClass"],
    }

}

def validate_manifest(data):
    try:
        validate(data, manifest_schema, format_checker=FormatChecker())
    except SchemaValidationError as e:
        message = f"Manifest error for field '{e.schema_path[-2]}': {e.message}"
        raise DjangoValidationError(message)
