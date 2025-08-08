from typing import Any

from qdrant_client import models

from mcp_server_qdrant.qdrant import ArbitraryFilter
from mcp_server_qdrant.settings import FilterableField


def make_filter(
    filterable_fields: dict[str, FilterableField], values: dict[str, Any]
) -> ArbitraryFilter:
    must_conditions = []
    must_not_conditions = []

    for raw_field_name, field_value in values.items():
        if raw_field_name not in filterable_fields:
            raise ValueError(f"Field {raw_field_name} is not a filterable field")

        field = filterable_fields[raw_field_name]

        if field_value is None:
            if field.required:
                raise ValueError(f"Field {raw_field_name} is required")
            else:
                continue

        # Support both nested metadata structure (original format) and flat structure (LlamaIndex format)
        field_name = raw_field_name

        if field.field_type == "keyword":
            if field.condition == "==":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == "!=":
                must_not_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == "any":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchAny(any=field_value)
                    )
                )
            elif field.condition == "except":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name,
                        match=models.MatchExcept(**{"except": field_value}),
                    )
                )
            elif field.condition is not None:
                raise ValueError(
                    f"Invalid condition {field.condition} for keyword field {field_name}"
                )

        elif field.field_type == "integer":
            if field.condition == "==":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == "!=":
                must_not_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == ">":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(gt=field_value)
                    )
                )
            elif field.condition == ">=":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(gte=field_value)
                    )
                )
            elif field.condition == "<":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(lt=field_value)
                    )
                )
            elif field.condition == "<=":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(lte=field_value)
                    )
                )
            elif field.condition == "any":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchAny(any=field_value)
                    )
                )
            elif field.condition == "except":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name,
                        match=models.MatchExcept(**{"except": field_value}),
                    )
                )
            elif field.condition is not None:
                raise ValueError(
                    f"Invalid condition {field.condition} for integer field {field_name}"
                )

        elif field.field_type == "float":
            # For float values, we only support range comparisons
            if field.condition == ">":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(gt=field_value)
                    )
                )
            elif field.condition == ">=":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(gte=field_value)
                    )
                )
            elif field.condition == "<":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(lt=field_value)
                    )
                )
            elif field.condition == "<=":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, range=models.Range(lte=field_value)
                    )
                )
            elif field.condition is not None:
                raise ValueError(
                    f"Invalid condition {field.condition} for float field {field_name}. "
                    "Only range comparisons (>, >=, <, <=) are supported for float values."
                )

        elif field.field_type == "boolean":
            if field.condition == "==":
                must_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition == "!=":
                must_not_conditions.append(
                    models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=field_value)
                    )
                )
            elif field.condition is not None:
                raise ValueError(
                    f"Invalid condition {field.condition} for boolean field {field_name}"
                )

        else:
            raise ValueError(
                f"Unsupported field type {field.field_type} for field {field_name}"
            )

    return models.Filter(
        must=must_conditions, must_not=must_not_conditions
    ).model_dump()


def make_indexes(
    filterable_fields: dict[str, FilterableField],
) -> dict[str, models.PayloadSchemaType]:
    indexes = {}

    for field_name, field in filterable_fields.items():
        # Create indexes for flat metadata structure (LlamaIndex format)
        if field.field_type == "keyword":
            indexes[field_name] = models.PayloadSchemaType.KEYWORD
        elif field.field_type == "integer":
            indexes[field_name] = models.PayloadSchemaType.INTEGER
        elif field.field_type == "float":
            indexes[field_name] = models.PayloadSchemaType.FLOAT
        elif field.field_type == "boolean":
            indexes[field_name] = models.PayloadSchemaType.BOOL
        else:
            raise ValueError(
                f"Unsupported field type {field.field_type} for field {field_name}"
            )

    return indexes
