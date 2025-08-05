import sys
from enum import Enum

if sys.version_info >= (3, 11):
    # Python 3.11 or higher
    from enum import EnumType
else:
    # Python < 3.11
    from enum import EnumMeta as EnumType

from typing import Any, Dict, List, Optional, Type, TypeVar, Union, overload

import pandas as pd

# pip install pint
import pint
import pint_pandas  # noqa: F401
from oold.model.v1 import LinkedBaseModelMetaClass as ModelMetaclass
from pydantic.v1 import Field, create_model
from pydantic.v1.fields import FieldInfo

from opensemantic import OswBaseModel

# import pint_pandas

# from osw.model.entity import Characteristic # pip install pint-pandas

QV = TypeVar("QV", bound="QuantityValue")


unit_registry: Dict[str, EnumType] = {}


class UnitEnumMetaclass(EnumType):
    def __new__(cls, clsname, bases, attrs):
        # print(attrs["__qualname__"], attrs)
        class_instance = EnumType.__new__(cls, clsname, bases, attrs)
        for key, value in attrs.items():
            if key not in ["__module__", "__qualname__", "_generate_next_value_"]:
                # register all enum values in the unit_registry
                if key in unit_registry:
                    pass
                    # warn(
                    #     (
                    #         f"Unit {key} already registered in "
                    #         "unit_registry, skip registration."
                    #     )
                    # )
                else:
                    unit_registry[key] = class_instance
        return class_instance


class UnitEnum(str, Enum, metaclass=UnitEnumMetaclass):
    pass


class Characteristic(OswBaseModel):
    """
    Elementary building block for object data schemas. Can inherit, reuse and/or define custom properties from other Characteristcs. Properties can have literal values or other complex values (objects) described by other Characteristics.
    """  # noqa: E501

    class Config:
        schema_extra = {
            "@context": [{"type": {"@id": "@type", "@type": "@id"}}],  # noqa: E501
            "uuid": "93ccae36-2435-42ce-ac6c-951450a81d47",  # noqa: E501
            "title": "Characteristic",  # noqa: E501
            "title*": {"en": "Characteristic", "de": "Charakteristik"},  # noqa: E501
            "description": "Elementary building block for object data schemas. Can inherit, reuse and/or define custom properties from other Characteristcs. Properties can have literal values or other complex values (objects) described by other Characteristics. ",  # noqa: E501
            "description*": {
                "en": "Elementary building block for object data schemas. Can inherit, reuse and/or define custom properties from other Characteristcs. Properties can have literal values or other complex values (objects) described by other Characteristics. ",  # noqa: E501
                "de": "Elementarer Baustein für Objekt-Datenschema. Kann Attribute von anderen Charakteristiken erben, übernehmen und/oder eigene definieren. Attribute können als Werte sowohl Literale als auch komplexe Objekte haben die von anderen Charakteristiken beschrieben werden.  ",  # noqa: E501
            },
        }

    type: Optional[List[str]] = Field(
        ["Category:OSW93ccae36243542ceac6c951450a81d47"],
        min_items=1,
        options={"hidden": True},
        propertyOrder=-1010,
        title="Types/Categories",
        title_={"de": "Typen/Kategorien"},
    )
    # should be optional:
    # uuid: UUID = Field(default_factory=uuid4, options={"hidden": True}, title="UUID")


ureg = pint.get_application_registry()

quantity_registry: Dict[EnumType, ModelMetaclass] = {}


class QuantityValueMetaclass(ModelMetaclass):
    def __new__(cls, clsname, bases, attrs):
        class_instance = super().__new__(cls, clsname, bases, attrs)
        # print(attrs["__qualname__"], attrs)
        if "unit" in attrs and attrs["unit"] is not None:
            # print(attrs["__annotations__"]["unit"].__dict__)#, attrs["unit"].__dict__)
            # print(attrs["unit"].__dict__["__objclass__"])
            # print(attrs["__annotations__"]["unit"].__args__[0])
            # register the mapping between the unit enum and the quantity class

            unit_field_type = None
            # check if FieldInfo was used for annotation
            if type(attrs["unit"]) is FieldInfo:
                _types = attrs["__annotations__"]["unit"].__args__
                # select the first type != None
                for _type in _types:
                    if _type is not None:
                        unit_field_type = _type
                        break
            else:
                unit_field_type = attrs["unit"].__dict__["__objclass__"]
            quantity_registry[unit_field_type] = class_instance
        return class_instance


class QuantityValue(Characteristic, metaclass=QuantityValueMetaclass):
    """
    A Quantity Value expresses the magnitude and kind of a quantity and is given by the product of a numerical value n and a unit of measure u (from qudt).
    """  # noqa: E501

    class Config:
        schema_extra = {
            "$comment": "Autogenerated section - do not edit. Generated from Category:Category Category:OSWffe74f291d354037b318c422591c5023",  # noqa: E501
            "uuid": "40829379-0663-4af9-92cf-9a1b18d772cf",
            "title": "QuantityValue",
            "title*": {"en": "Quantity Value"},
            "description": "A Quantity Value expresses the magnitude and kind of a quantity and is given by the product of a numerical value n and a unit of measure u (from qudt).",  # noqa: E501
            "description*": {
                "en": "A Quantity Value expresses the magnitude and kind of a quantity and is given by the product of a numerical value n and a unit of measure u (from qudt)."  # noqa: E501
            },
            "defaultProperties": ["type", "unit"],
            "@context": [
                "/wiki/Category:OSW93ccae36243542ceac6c951450a81d47?action=raw&slot=jsonschema",  # noqa: E501
                {"unit": "Property:HasUnit", "value": "Property:HasValue"},
            ],
            "$defs": {},
        }

    type: Optional[Any] = ["Category:OSW4082937906634af992cf9a1b18d772cf"]
    value: float = Field(
        ...,
        options={"grid_columns": 4},
        title="value",
        title_={"en": "Value", "de": "Wert"},
    )
    unit: Optional[UnitEnum] = Field(
        None,
        options={"grid_columns": 4},
        title="unit",
        title_={"en": "Unit", "de": "Einheit"},
    )

    # fmt: off
    @overload
    def __init__(self, value: float, unit: Optional[UnitEnum]) -> None:
        ...

    @overload
    def __init__(self, v: float, u: Optional[UnitEnum]) -> None:
        ...

    @overload
    def __init__(self, quantity_value: "QuantityValue") -> None:
        ...

    @overload
    def __init__(
        self, pint_quantity: pint.Quantity, quantity_type: Type["QuantityValue"]
    ) -> None:
        ...

    # @overload
    # def __init__(self, **data: Any) -> None:
    #     ...
    # fmt: on

    def __init__(self, *args, **kwargs) -> None:
        if "v" in kwargs or "u" in kwargs:
            # support for v, u as keyword arguments
            kwargs["value"] = kwargs.pop("v")
            kwargs["unit"] = kwargs.pop("u")
            # will raise error if alias and original names are mixed
        elif (
            len(args) == 2
            and isinstance(args[0], float)
            and isinstance(args[1], UnitEnum)
        ):
            # support for float, UnitEnum as positional arguments
            raise AttributeError(
                "QuantityValue.__init__() takes either a pint.Quantity and "
                "QuantityValue subclass as positional arguments, or a QuantityValue "
                "as positional arguments, but not a float and UnitEnum. These are "
                "keyword arguments only!"
            )
        elif (
            len(args) == 2
            and isinstance(args[0], pint.Quantity)
            and issubclass(args[1], QuantityValue)
        ):
            # support for pint.Quantity and Type[QuantityValue] as positional arguments
            qv_dict = QuantityValue.from_pint(
                quantity=args[0], simplify=True, quantity_type=args[1], return_dict=True
            )
            kwargs["value"] = qv_dict["value"]
            kwargs["unit"] = qv_dict["unit"]

        elif "pint_quantity" in kwargs and "quantity_type" in kwargs:
            # support for pint.Quantity and Type[QuantityValue] as keyword arguments
            qv_dict = QuantityValue.from_pint(
                quantity=kwargs.pop("pint_quantity"),
                simplify=True,
                quantity_type=kwargs.pop("quantity_type"),
                return_dict=True,
            )
            kwargs["value"] = qv_dict["value"]
            kwargs["unit"] = qv_dict["unit"]
        elif "pint_quantity" in kwargs and "quantity_type" not in kwargs:
            raise ValueError(
                "If 'pint_quantity' is provided, a 'quantity_type' to cast to must "
                "also be provided."
            )
        elif len(args) == 1 and len(kwargs) == 0 and isinstance([0], QuantityValue):
            # support for QuantityValue as positional argument
            kwargs = args[0].dict()
        elif "quantity_value" in kwargs:
            # support for QuantityValue as keyword argument
            quantity_value = kwargs.pop("quantity_value")
            kwargs["value"] = quantity_value.value
            kwargs["unit"] = quantity_value.unit

        super().__init__(**kwargs)

    @classmethod
    def get_pint_ureg_compatible_str(cls, string: str) -> str:
        pint_unit_name = string.replace("_", " ")
        # SI prefixes, see https://en.wikipedia.org/wiki/Metric_prefix
        prefixes = [
            "quetta",
            "ronna",
            "yotta",
            "zetta",
            "exa",
            "peta",
            "tera",
            "giga",
            "mega",
            "kilo",
            "hecto",
            "deca",
            "deci",
            "centi",
            "milli",
            "micro",
            "nano",
            "pico",
            "femto",
            "atto",
            "zepto",
            "yocto",
            "ronto",
            "quecto",
        ]

        for prefix in prefixes:
            pint_unit_name = pint_unit_name.replace(prefix + " ", prefix)
        if pint_unit_name.split(" ")[0] == "per":
            pint_unit_name = pint_unit_name.replace("per", "1 /")
        return pint_unit_name

    def to_pint(self) -> pint.Quantity:
        pint_unit_name = QuantityValue.get_pint_ureg_compatible_str(self.unit.name)

        return self.value * ureg[pint_unit_name]

    # fmt: on
    @classmethod
    @overload
    def from_pint(
        cls: Type[QV],
        quantity: pint.Quantity,
        simplify: bool = ...,
        quantity_type: Optional[Type[QV]] = ...,
        return_dict: bool = False,
    ) -> QV: ...

    @classmethod
    @overload
    def from_pint(
        cls: Type[QV],
        quantity: pint.Quantity,
        simplify: bool = ...,
        quantity_type: Optional[Type[QV]] = ...,
        return_dict: bool = True,
    ) -> Dict[str, Any]: ...

    # fmt: off

    @classmethod
    def from_pint(
        cls: Type[QV],
        quantity: pint.Quantity,
        simplify: bool = True,
        quantity_type: Optional[Type[QV]] = None,
        return_dict: bool = False,
    ) -> Union[QV, Dict[str, Any]]:
        # see also
        # https://pint.readthedocs.io/en/stable/getting/tutorial.html#simplifying-units
        # unit_symbol = "{:~P}".format(quantity.units)
        if quantity_type and not issubclass(quantity_type, QuantityValue):
            raise ValueError(
                f"Provided quantity_type '{quantity_type}' is not a subclass of "
                f"QuantityValue."
            )

        def original(quantity_: pint.Quantity):
            if simplify:
                value = (
                    f"{quantity_:9f#Lx}"  # 9f => round to 8 digits, '#' => simplify
                    # the unit
                )
            else:
                value = f"{quantity_:9fLx}"
            # e.g. \SI[]{1.0}{\kilo\gram\meter\per\ampere\squared\per\second\squared}
            # select the last curly brace
            unit_symbol = value.split("{")[-1].replace("}", "")
            # replace backslashes with underscores
            unit_symbol = unit_symbol.replace("\\", "_").strip("_")
            # nummeric_value = quantity.magnitude
            # simplifying the unit may change the scale
            nummeric_value = float(value.split("{")[1].split("}")[0])
            if len(unit_symbol) == 0:
                unit_symbol = "dimensionless"
            unit_class = unit_registry[unit_symbol]
            quantity_class = quantity_registry[unit_class]
            if quantity_type is not None:
                # if a specific quantity type is provided, use it instead of the
                # default one
                quantity_class = quantity_type
            if return_dict:
                return {
                    "value": nummeric_value,
                    "unit": unit_class[unit_symbol],
                    "quantity_type": quantity_class,
                }
            return quantity_class(value=nummeric_value, unit=unit_class[unit_symbol])

        def altered(quantity_: pint.Quantity):
            """
            Converts a Pint Quantity to base units (removing prefixes),
            and returns a LaTeX-formatted string with adjusted numeric value.
            """
            # Convert to base units to remove prefixes
            base_quantity = quantity_.to_base_units()

            # Format the numeric value and unit separately
            nummeric_value = base_quantity.magnitude
            unit_latex = f"{base_quantity.units:Lx}"
            if simplify:
                unit_latex = f"{base_quantity.units:#Lx}"

            unit_symbol_1 = unit_latex.split("{")[-1].replace("}", "")
            unit_symbol_2 = unit_symbol_1.replace("\\", "_").strip("_")
            if len(unit_symbol_2) == 0:
                unit_symbol_2 = "dimensionless"
            unit_class = unit_registry[unit_symbol_2]
            quantity_class = quantity_registry[unit_class]
            if quantity_type is not None:
                # if a specific quantity type is provided, use it instead of the
                # default one
                quantity_class = quantity_type
            if return_dict:
                return {
                    "value": nummeric_value,
                    "unit": unit_class[unit_symbol_2],
                    "quantity_type": quantity_class,
                }
            return quantity_class(value=nummeric_value, unit=unit_class[unit_symbol_2])

        try:
            return original(quantity)
        except KeyError:
            return altered(quantity)

    def to_base(self) -> "QuantityValue":
        """Converts the QuantityValue to its base unit."""
        pint_quantity = self.to_pint().to_base_units()
        return QuantityValue.from_pint(pint_quantity, simplify=False)

    def to_unit(self, unit: Union[UnitEnum, str]) -> "QuantityValue":
        """Converts the QuantityValue to the specified unit."""

        if isinstance(unit, UnitEnum):
            unit_str = QuantityValue.get_pint_ureg_compatible_str(unit.name)
        elif isinstance(unit, str):
            # Assuming the string is a valid unit from the pint unit registry
            unit_str = QuantityValue.get_pint_ureg_compatible_str(unit)
        else:
            raise ValueError(
                f"Invalid unit type: {type(unit)}. Must be UnitEnum or str.")

        pint_quantity = self.to_pint().to(unit_str)
        return QuantityValue.from_pint(
            quantity=pint_quantity, simplify=False, quantity_type=self.__class__)

    def __neg__(self) -> "QuantityValue":
        return QuantityValue.from_pint(-self.to_pint())

    def __pos__(self) -> "QuantityValue":
        return QuantityValue.from_pint(+self.to_pint())

    def __abs__(self) -> "QuantityValue":
        return QuantityValue.from_pint(abs(self.to_pint()))

    def __add__(self, other: "QuantityValue") -> "QuantityValue":
        res_pint = self.to_pint() + other.to_pint()
        return QuantityValue.from_pint(res_pint)

    def __sub__(self, other: "QuantityValue") -> "QuantityValue":
        res_pint = self.to_pint() - other.to_pint()
        return QuantityValue.from_pint(res_pint)

    # * operator
    def __mul__(self, other: Union["QuantityValue", float, int]) -> "QuantityValue":
        if not isinstance(other, (float, int)):
            other = other.to_pint()
        res_pint = self.to_pint() * other
        return QuantityValue.from_pint(res_pint)

    # / operator
    def __truediv__(self, other: Union["QuantityValue", float, int]) -> "QuantityValue":
        if not isinstance(other, (float, int)):
            other = other.to_pint()
        res_pint = self.to_pint() / other
        return QuantityValue.from_pint(res_pint)

    def __floordiv__(self, other: "QuantityValue") -> "QuantityValue":
        """Floor division is supported by pint only for dimensionless quantities and
        quantities with the same dimension"""
        if isinstance(other, QuantityValue):
            other = other.to_pint()
        return QuantityValue.from_pint(self.to_pint() // other)

    def __mod__(self, other: "QuantityValue") -> "QuantityValue":
        """Modulo is supported by pint only for dimensionless quantities and
        quantities with the same dimension"""
        if isinstance(other, QuantityValue):
            other = other.to_pint()
        return QuantityValue.from_pint(self.to_pint() % other)

    def __pow__(self, other: Union[int, float, "QuantityValue"]) -> "QuantityValue":
        # todo: test if supported with dimensionless unit / quantity
        if isinstance(other, QuantityValue):
            other = other.to_pint()
        return QuantityValue.from_pint(self.to_pint() ** other)

    def __eq__(self, other: "QuantityValue") -> bool:
        return self.to_pint() == other.to_pint()

    def __ne__(self, other: "QuantityValue") -> bool:
        return self.to_pint() != other.to_pint()

    def __ge__(self, other: "QuantityValue") -> bool:
        return self.to_pint() >= other.to_pint()

    def __gt__(self, other: "QuantityValue") -> bool:
        return self.to_pint() > other.to_pint()

    def __le__(self, other: "QuantityValue") -> bool:
        return self.to_pint() <= other.to_pint()

    def __lt__(self, other: "QuantityValue") -> bool:
        return self.to_pint() < other.to_pint()


QuantityValue.update_forward_refs()


class TabularData(OswBaseModel):
    # rows: List[Any] # convention for tabular data is a list of rows

    # consider https://stackoverflow.com/questions/51505504/pandas-nesting-dataframes # noqa: E501
    # consider https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.attrs.html # noqa: E501

    def to_df(self) -> pd.DataFrame:
        series = []
        row_class = self.__class__.__fields__["rows"].type_
        for attr in row_class.__fields__.keys():
            q_name = (
                row_class.__fields__[attr]
                .type_.__fields__["unit"]
                .default.name.replace("_", " ")
            )
            # q_pint = ureg[q_name]
            s = pd.Series(
                [
                    (
                        getattr(m, attr).to_pint().to(q_name).magnitude
                        if getattr(m, attr, None) is not None
                        else None
                    )
                    for m in self.rows
                ],
                dtype="pint[" + q_name + "]",
                name=attr,
            )
            series.append(s)
        rows = {s.name: s for s in series}
        return pd.DataFrame(rows)

    @classmethod
    def from_df(cls, df: pd.DataFrame):
        rows = []
        row_class = OswBaseModel
        if "rows" in cls.__fields__:
            row_class = cls.__fields__["rows"].type_

        additional_fields = {}
        for key in df.columns:
            # print(df[key].pint.__dict__)
            if key not in row_class.__fields__.keys():
                # raise ValueError(f"Column '{key}' not found in '{row_class.__name__}'") # noqa: E501
                quantity = QuantityValue.from_pint(
                    1 * getattr(df.dtypes, key).units
                ).__class__
                additional_fields[key] = (quantity, ...)

        if len(additional_fields) > 0:
            row_class = create_model(
                row_class.__name__ + "Extended", **additional_fields, __base__=row_class
            )
            cls = create_model(
                cls.__name__ + "Extended",
                **{"rows": (List[row_class], ...)},
                __base__=cls,
            )

        # convert all columns to the default unit
        for attr in row_class.__fields__.keys():
            q_name = (
                row_class.__fields__[attr]
                .type_.__fields__["unit"]
                .default.name.replace("_", " ")
            )
            q_pint = ureg[q_name]
            df[attr] = df[attr].pint.to(q_pint)

        for i, row in df.iterrows():
            # create a dictionary with the values of the row
            # using the column names as keys
            d = {key: {"value": row[key].magnitude} for key in df.columns}
            m = row_class(**d)
            rows.append(m)
        return cls(rows=rows)
