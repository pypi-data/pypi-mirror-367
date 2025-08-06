import enum
import random
import uuid
from datetime import date, datetime
from enum import Enum
from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from faker import Faker
from pydantic import UUID4, BaseModel, StrictFloat
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

faker = Faker()


def _generate_unique_string(pattern: str, max_length: int) -> str:
    """Generate a unique string based on a pattern containing '<unique>'"""
    import hashlib
    import time
    import uuid

    # Replace "<unique>" with a truly unique identifier
    if "<unique>" in pattern:
        # Calculate the base pattern (without <unique>)
        base_pattern = pattern.replace("<unique>", "")

        # If the base pattern is already longer than max_length, truncate it
        if len(base_pattern) > max_length:
            return base_pattern[:max_length]

        # Calculate available space for unique part
        available_length = max_length - len(base_pattern)

        # Calculate timestamp and hash once for all strategies
        timestamp = int(time.time() * 1000000)
        timestamp_hash = hashlib.md5(str(timestamp).encode()).hexdigest()

        # Choose strategy based on available space
        if available_length >= 20:
            # Use timestamp + UUID for maximum uniqueness
            unique_id = uuid.uuid4().hex[:8]
            unique_part = f"{timestamp}_{unique_id}"
        elif available_length >= 12:
            # Use 12 characters of hashed timestamp
            unique_part = timestamp_hash[:12]
        elif available_length >= 8:
            # Use 8 characters of hashed timestamp
            unique_part = timestamp_hash[:8]
        elif available_length >= 6:
            # Use 6 characters of hashed timestamp
            unique_part = timestamp_hash[:6]
        elif available_length > 0:
            # Use whatever space is available
            unique_part = timestamp_hash[:available_length]
        else:
            # If no space available, return just the base pattern
            return base_pattern

        result = pattern.replace("<unique>", unique_part)
        return result

    return pattern


def _extract_field_constraints(field_info: FieldInfo) -> Dict[str, Any]:
    """Extract constraints from Pydantic FieldInfo"""
    constraints = {}

    # Handle Pydantic 2.x metadata-based constraints
    if hasattr(field_info, "metadata") and field_info.metadata:
        for constraint in field_info.metadata:
            constraint_type = type(constraint).__name__
            if constraint_type == "MaxLen":
                constraints["max_length"] = constraint.max_length
            elif constraint_type == "MinLen":
                constraints["min_length"] = constraint.min_length
            elif constraint_type == "Ge":
                constraints["min_value"] = constraint.ge
            elif constraint_type == "Le":
                constraints["max_value"] = constraint.le
            elif constraint_type == "Gt":
                constraints["min_value"] = constraint.gt + 1
            elif constraint_type == "Lt":
                constraints["max_value"] = constraint.lt - 1

    # Fallback to direct attributes (Pydantic 1.x style)
    if hasattr(field_info, "max_length") and field_info.max_length is not None:
        constraints["max_length"] = field_info.max_length
    if hasattr(field_info, "min_length") and field_info.min_length is not None:
        constraints["min_length"] = field_info.min_length
    if hasattr(field_info, "ge") and field_info.ge is not None:
        constraints["min_value"] = field_info.ge
    if hasattr(field_info, "le") and field_info.le is not None:
        constraints["max_value"] = field_info.le
    if hasattr(field_info, "gt") and field_info.gt is not None:
        constraints["min_value"] = field_info.gt + 1
    if hasattr(field_info, "lt") and field_info.lt is not None:
        constraints["max_value"] = field_info.lt - 1

    return constraints


def _handle_literal_type(field_type: Any) -> Any:
    """Handle Literal types by choosing from allowed values"""
    if get_origin(field_type) is Literal:
        literal_values = get_args(field_type)
        return random.choice(literal_values)
    return None


def _generate_constrained_string(field_name: str, constraints: Dict[str, Any]) -> str:
    """Generate string respecting length constraints"""
    min_length = constraints.get("min_length", 1)
    max_length = constraints.get("max_length", 50)

    # Use field name heuristics when possible, but ensure constraints are respected
    field_name_lower = field_name.lower()

    # Try field-specific generation first
    if "email" in field_name_lower and max_length >= 7:  # minimum for "a@b.com"
        base_value = faker.email()
        if len(base_value) > max_length:
            # Generate a shorter email that fits
            username = faker.user_name()[
                : max(1, max_length - 6)
            ]  # Leave room for "@x.com"
            base_value = f"{username}@{faker.random_letter()}.com"
            if len(base_value) > max_length:
                base_value = f"a@{faker.random_letter()}.co"[:max_length]
    elif "name" in field_name_lower:
        base_value = faker.name()
        if len(base_value) > max_length:
            base_value = faker.first_name()
            if len(base_value) > max_length:
                base_value = faker.first_name()[:max_length]
    elif "url" in field_name_lower and max_length >= 10:
        base_value = faker.url()
        if len(base_value) > max_length:
            base_value = f"http://{faker.word()}.com"[:max_length]
    elif "phone" in field_name_lower and max_length >= 10:
        base_value = faker.phone_number()
        if len(base_value) > max_length:
            base_value = faker.phone_number()[:max_length]
    elif "description" in field_name_lower:
        # For description fields, generate longer text but respect explicit constraints
        if not constraints or "max_length" not in constraints:
            # No explicit constraints, generate longer description text
            max_length = 120  # Override default for descriptions
            base_value = faker.text(max_nb_chars=120)
        else:
            # Has explicit max_length constraint
            base_value = faker.text(max_nb_chars=max_length)
        base_value = base_value.rstrip(".\n ")
    elif "street" in field_name_lower or "address" in field_name_lower:
        base_value = faker.street_address()
        if len(base_value) > max_length:
            base_value = faker.street_address()[:max_length]
    elif "city" in field_name_lower:
        base_value = faker.city()
        if len(base_value) > max_length:
            base_value = faker.city()[:max_length]
    elif (
        "state" in field_name_lower
        or "province" in field_name_lower
        or "region" in field_name_lower
    ):
        # For state/province fields, use full state name or abbreviation based on max_length
        if max_length <= 3:
            base_value = faker.state_abbr()
        else:
            base_value = faker.state()
            if len(base_value) > max_length:
                base_value = faker.state_abbr()
    elif "country" in field_name_lower:
        base_value = faker.country()
        if len(base_value) > max_length:
            # If country name is too long, try country code
            base_value = faker.country_code()
            if len(base_value) > max_length:
                base_value = faker.country()[:max_length]
    elif "zip" in field_name_lower or "postal" in field_name_lower:
        base_value = faker.postcode()
        if len(base_value) > max_length:
            base_value = faker.postcode()[:max_length]
    else:
        # General string generation with length awareness
        if max_length <= 5:
            base_value = faker.lexify("?????")[:max_length]
        elif max_length <= 10:
            base_value = faker.word()
            if len(base_value) > max_length:
                base_value = faker.lexify("?" * max_length)
        elif max_length <= 20:
            words = faker.words(nb=2)
            base_value = " ".join(words)
            if len(base_value) > max_length:
                base_value = faker.words(nb=1)[0]
                if len(base_value) > max_length:
                    base_value = faker.lexify("?" * max_length)
        else:
            base_value = faker.text(max_nb_chars=max_length)
            base_value = base_value.rstrip(".\n ")

    # Ensure we don't exceed max_length
    if len(base_value) > max_length:
        base_value = base_value[:max_length]

    # Pad to meet min_length if needed
    if len(base_value) < min_length:
        padding_needed = min_length - len(base_value)
        padding = "".join(faker.random_letter() for _ in range(padding_needed))
        base_value = base_value + padding

    return base_value


def _generate_constrained_number(
    field_type: Type, field_name: str, constraints: Dict[str, Any]
) -> Union[int, float]:
    """Generate numbers respecting range constraints"""
    # Special handling for year fields
    if "year" in field_name.lower() and field_type is int:
        current_year = datetime.now().year
        min_val = constraints.get("min_value", 1900)
        max_val = constraints.get("max_value", current_year + 10)
        return faker.random_int(min=int(min_val), max=int(max_val))

    # General numeric constraints
    if field_type is int:
        min_val = constraints.get("min_value", 0)
        max_val = constraints.get("max_value", 100)
        return faker.random_int(min=int(min_val), max=int(max_val))
    else:
        min_val = constraints.get("min_value", 0.0)
        max_val = constraints.get("max_value", 100.0)
        return round(
            faker.pyfloat(min_value=float(min_val), max_value=float(max_val)), 2
        )


def _get_prioritized_union_type(types: List[Type]) -> Type:
    """
    Select the most appropriate type from a Union for fake data generation.

    Prioritization order (highest to lowest priority):
    1. Literal types (most specific)
    2. Enum types (domain-specific values)
    3. datetime/date types (structured temporal data)
    4. bool types (more specific than str)
    5. Numeric types (int, float - more specific than str)
    6. UUID types (structured data)
    7. str (fallback, least specific)
    """
    # Priority 1: Literal types (most specific constraints)
    literal_types = [t for t in types if get_origin(t) is Literal]
    if literal_types:
        return literal_types[0]

    # Priority 2: Enum types (domain-specific values)
    enum_types = [t for t in types if isinstance(t, type) and issubclass(t, Enum)]
    if enum_types:
        return enum_types[0]

    # Priority 3: datetime/date types (structured temporal data)
    datetime_types = [t for t in types if t in (datetime, date)]
    if datetime_types:
        return datetime_types[0]

    # Priority 4: bool types (more specific than str)
    bool_types = [t for t in types if t is bool]
    if bool_types:
        return bool_types[0]

    # Priority 5: Numeric types (more specific than str)
    numeric_types = [t for t in types if t in (int, float)]
    if numeric_types:
        return numeric_types[0]

    # Priority 6: UUID types (structured data)
    uuid_types = [t for t in types if t in (uuid.UUID, UUID4)]
    if uuid_types:
        return uuid_types[0]

    # Priority 7: Fallback to first type (includes str and others)
    return types[0]


def _faux_value(
    field_type: Any, field_name: str = "", field_info: FieldInfo = None
) -> Any:
    # Handle None or PydanticUndefined field types
    if field_type is None or field_type is PydanticUndefined:
        return faker.word()

    # Extract constraints if field_info provided
    constraints = {}
    if field_info:
        constraints = _extract_field_constraints(field_info)

    # Handle Literal types first
    literal_value = _handle_literal_type(field_type)
    if literal_value is not None:
        return literal_value

    # Handle Annotated types
    if get_origin(field_type) is Annotated:
        field_type = get_args(field_type)[0]

    # Get the origin type (e.g., List from List[str])
    origin = get_origin(field_type)
    args = get_args(field_type)

    # Handle Union types (including Optional) and new union operator (|)
    # UnionType is available in Python 3.10+, TypeAliasType in Python 3.12+
    union_types = (Union,)
    try:
        from types import UnionType

        union_types = (Union, UnionType)
    except ImportError:
        pass

    try:
        from types import TypeAliasType

        union_types = union_types + (TypeAliasType,)
    except ImportError:
        pass

    if origin in union_types:
        # Filter out None for Optional types
        types = [t for t in args if t is not type(None)]
        if types:
            # Use prioritized type selection for better fake data generation
            prioritized_type = _get_prioritized_union_type(types)
            return _faux_value(prioritized_type, field_name, field_info)
        return None

    # Handle List types
    if origin is list:
        item_type = args[0] if args else Any
        return [_faux_value(item_type, field_name) for _ in range(random.randint(1, 3))]

    # Handle Dict types
    if origin is dict:
        key_type = args[0] if args else str
        value_type = args[1] if len(args) > 1 else Any
        return {
            _faux_value(key_type, f"{field_name}_key"): _faux_value(
                value_type, f"{field_name}_value"
            )
            for _ in range(random.randint(1, 3))
        }

    # Handle basic types
    if isinstance(field_type, type):
        if issubclass(field_type, BaseModel):
            return faux_dict(field_type)
        elif issubclass(field_type, Enum):
            return random.choice(list(field_type))
        elif field_type is str:
            return _generate_constrained_string(field_name, constraints)
        elif field_type is int:
            return _generate_constrained_number(field_type, field_name, constraints)
        elif field_type is float:
            return _generate_constrained_number(field_type, field_name, constraints)
        elif field_type is bool:
            return faker.boolean()
        elif field_type is datetime:
            return faker.date_time()
        elif field_type is date:
            return date.fromisoformat(faker.date())
        elif field_type is uuid.UUID or field_type is UUID4:
            return uuid.UUID(faker.uuid4())
        elif field_type is dict:
            # Handle plain dict type (without type parameters)
            return {
                _faux_value(str, f"{field_name}_key"): _faux_value(
                    Any, f"{field_name}_value"
                )
                for _ in range(random.randint(1, 3))
            }
        elif field_type is list:
            # Handle plain list type (without type parameters)
            return [
                _faux_value(Any, f"{field_name}_item")
                for _ in range(random.randint(1, 3))
            ]
        elif field_type is tuple:
            # Handle plain tuple type (without type parameters)
            return tuple(
                _faux_value(Any, f"{field_name}_item")
                for _ in range(random.randint(1, 3))
            )
        elif field_type is set:
            # Handle plain set type (without type parameters)
            return {
                _faux_value(Any, f"{field_name}_item")
                for _ in range(random.randint(1, 3))
            }
        elif field_type is frozenset:
            # Handle plain frozenset type (without type parameters)
            return frozenset(
                _faux_value(Any, f"{field_name}_item")
                for _ in range(random.randint(1, 3))
            )
        elif field_type is bytes:
            # Handle bytes type
            return faker.binary(length=random.randint(10, 50))
        elif field_type is complex:
            # Handle complex type
            return complex(faker.random_number(), faker.random_number())

    # Handle FieldInfo objects
    if isinstance(field_type, FieldInfo):
        return _faux_value(field_type.annotation, field_name, field_type)

    # Default fallback
    return faker.word()


def _process_unique_value(value: Any, field_info: FieldInfo = None) -> Any:
    """Process a value to handle unique string patterns"""
    if isinstance(value, str) and "<unique>" in value:
        constraints = {}
        if field_info:
            constraints = _extract_field_constraints(field_info)
        max_length = constraints.get("max_length", 50)
        return _generate_unique_string(value, max_length)
    return value


def faux_dict(model: Type[BaseModel], **kwargs: Any) -> Dict[str, Any]:
    model_values: Dict[str, Any] = {}

    for name, field_info in model.model_fields.items():
        if name in kwargs:
            # Process unique values in kwargs
            model_values[name] = _process_unique_value(kwargs[name], field_info)
            continue

        # Pass both type and field info for constraint-aware generation
        model_values[name] = _faux_value(field_info.annotation, name, field_info)

    return model_values


Model = TypeVar("Model", bound=BaseModel)


def faux(pydantic_model: Type[Model], **kwargs: Any) -> Model:
    return pydantic_model(**faux_dict(pydantic_model, **kwargs))
