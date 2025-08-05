import json

import pint

import opensemantic.characteristics.quantitative._model as q
from opensemantic.characteristics.quantitative._static import quantity_registry


def test_addition():
    q1 = q.Mobility(
        value=1.0,
        unit=q.MobilityUnit.meter_squared_per_second_per_volt,
    )

    q2 = q.Mobility(
        value=1.0,
        unit=q.MobilityUnit.centi_meter_squared_per_second_per_volt,
    )

    q3 = q1 + q2
    assert (
        q3.value == 1.0001
        and q3.unit == q.MobilityUnit.meter_squared_per_second_per_volt
    )


def test_quantity_value():
    q1 = q.Length(value=1.0, unit=q.LengthUnit.milli_meter)

    q_json = json.loads(q1.json(exclude_none=True))
    # print(q_json)
    assert q_json == {
        "type": ["Category:OSWee9c7e5c343e542cb5a8b4648315902f"],
        "value": 1.0,
        "unit": (
            "Item:OSWf101d25e944856e3bd4b4c9863db7de2"
            "#OSW322dec469be75aedb008b3ebff29db86"
        ),
    }

    q1 = q.Length(value=1.0, unit=q.LengthUnit.meter)

    q_json = json.loads(q1.json(exclude_none=True))
    # print(q_json)
    assert q_json == {
        "type": ["Category:OSWee9c7e5c343e542cb5a8b4648315902f"],
        "value": 1.0,
        "unit": "Item:OSWf101d25e944856e3bd4b4c9863db7de2",
    }

    q_json = json.loads(q1.json(exclude_none=True, exclude_defaults=True))
    # print(q_json)
    assert q_json == {"value": 1.0}


def test_pint():
    q1 = q.Length(value=1.0, unit=q.LengthUnit.milli_meter)
    # transform to pint
    q_pint = q1.to_pint()
    # transform back to QuantityValue
    q_ = q.QuantityValue.from_pint(q_pint)
    assert q1 == q_

    q2 = q.Length(value=1.0, unit=q.LengthUnit.meter)
    q3 = q1 + q2
    assert q3 == q.Length(value=1.001, unit=q.LengthUnit.meter)

    q31 = q1 * q2
    assert q31 == q.Area(value=1000.0, unit=q.AreaUnit.milli_meter_squared)

    q41 = q.Area(value=1.0, unit=q.AreaUnit.meter_squared)
    q42 = q.Area(value=1.0, unit=q.AreaUnit.milli_meter_squared)
    # 'square_meter' is not a valid unit for pint, but 'square_meter' is
    q43 = q41 + q42
    assert q43 == q.Area(value=1.000001, unit=q.AreaUnit.meter_squared)

    q5 = q.Length(value=2.0, unit=q.LengthUnit.meter)
    q25 = q2 / q5  # Dimensionless(value=0.5, unit=DimensionLessUnit.dimensionless)
    # will envoke QuantityValue.from_pint(), which will call unit_registry[unit_symbol]
    _ = q.VoltageRatio(value=q25.value)


def test_full_inventory_test():
    # test all QuantityValue classes
    warning_count = 0
    critical_warning_count = 0
    error_count = 0
    success_count = 0
    qu_reg = {}
    # build a list of all UnitEnums per QuantityValue class
    for ue, qv in quantity_registry.items():
        if qv not in qu_reg:
            qu_reg[qv] = []
        qu_reg[qv].append(ue)

    # build a list of all entr

    for qv in qu_reg.keys():
        # round-trip to and from pint
        # interate of the ue Enum members

        for ue in qu_reg[qv]:
            for u in ue:
                # create a QuantityValue object
                q1 = qv(value=1.0, unit=u)

                try:
                    # transform to pint
                    q_pint = q1.to_pint()
                    # transform back to QuantityValue
                    q_ = q.QuantityValue.from_pint(q_pint)
                    # assert q1 == q_
                    if q1 != q_:
                        # print(
                        # (
                        # f"Warning: {q1.value} {q1.unit} ",
                        # f"!= {q_.value} {q_.unit}",
                        # )
                        # )
                        warning_count += 1
                        # print(q1.to_pint())
                        # print(q_.to_pint())
                        if type(q1) is not type(q_):
                            print(
                                (
                                    f"Critical Warning: {q1.__class__.__name__} "
                                    f"and {q_.__class__.__name__} "
                                    f"have the same unit {u}"
                                )
                            )
                            critical_warning_count += 1
                            pass
                        elif q1.unit != q_.unit:
                            print(f"Warning: {q1.unit} was normalized to {q_.unit}")
                            pass
                        elif q1.value != q_.value:
                            print(f"Warning: Rounding error: {q1.value} vs {q_.value}")
                            pass
                        else:
                            print(f"Warning: Unknown error: {q1} vs {q_}")
                            pass

                    else:
                        success_count += 1
                except Exception as e:
                    # check if e is of type pint.errors.UndefinedUnitError
                    if isinstance(e, pint.errors.UndefinedUnitError):
                        print(f"Error: Missing unit {u} in pint")
                    elif isinstance(e, KeyError):
                        print(f"Error: Missing unit {u} in unit_registry")
                    else:
                        print(f"Error {e.__class__}: {q1} -> {q_pint} -> {q_}")
                        # print(re
                    error_count += 1
    print(
        (
            f"{success_count} successful, "
            f"{error_count} errors and {warning_count} warnings "
            f"({critical_warning_count} critical)"
        )
    )
    # 283 successful, 366 errors and 300 warnings # baseline
    # 295 successful, 292 errors and 362 warnings # fix inverse units
    # 346 successful, 122 errors and 481 warnings # fix SI prefixes
    # 359 successful, 105 errors and 485 warnings (444 critical) # fix all inverse


if __name__ == "__main__":
    test_addition()
    test_quantity_value()
    test_pint()
    test_full_inventory_test()

# pint_reg = pint.UnitRegistry()
# pint_q = pint_reg.Quantity(1.0, "petajoule")
# # not defined, try alias
# pint_q = pint_reg.Quantity(1.0, "joule 1 / kelvin 1 / kilogram squared 1 / pascal")
# print(pint_q)
# print(f"{pint_q:9f#Lx}")

# naming collisions?
# VaporPermeability
# NEONUnit
# CombinedNonEvaporativeHeatTransferCoefficient
