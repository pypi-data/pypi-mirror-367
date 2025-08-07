from __future__ import annotations

from datetime import datetime

import bytewax.operators as op
from bytewax.dataflow import Dataflow
from bytewax.testing import TestingSink, TestingSource, run_main
from pandas import DataFrame, DatetimeIndex, isna

from nortech.datatools.handlers.pandas import get_df
from nortech.datatools.values.windowing import TimeWindow
from nortech.derivers.services.nortech_api import deploy_deriver as deploy_deriver_api
from nortech.derivers.values.deriver import Deriver
from nortech.gateways.nortech_api import NortechAPI


def deploy_deriver(
    nortech_api: NortechAPI,
    deriver: type[Deriver],
    start_at: datetime | None = None,
    create_parents: bool = False,
):
    return deploy_deriver_api(
        nortech_api=nortech_api,
        deriver=deriver,
        start_at=start_at,
        create_parents=create_parents,
    )


def run_deriver_locally(
    nortech_api: NortechAPI,
    deriver: type[Deriver],
    batch_size: int = 10000,
    df: DataFrame | None = None,
    time_window: TimeWindow | None = None,
):
    if time_window is not None:
        inputs = deriver.Inputs.list()
        df = get_df(nortech_api, signals=[_input for _, _input in inputs], time_window=time_window)
        path_to_name = {_input.path: name for name, _input in inputs}
        df = df.rename(columns=path_to_name)

    elif df is not None:
        df = df
    else:
        raise ValueError("Either df or time_window must be provided")

    if not isinstance(df.index, DatetimeIndex):
        raise ValueError("df must have a datetime index")

    df_timezone = df.index.tz
    df.index = df.index.tz_convert("UTC")

    def df_to_inputs(df: DataFrame):
        for deriver_input in df.reset_index().to_dict("records"):
            input_with_none = {k: (None if isna(v) else v) for k, v in deriver_input.items()}
            yield deriver.Inputs.model_validate(input_with_none)

    source = TestingSource(ib=df_to_inputs(df), batch_size=batch_size)
    flow = Dataflow(deriver.__name__)
    stream = op.input("input", flow, source)
    transformed_stream = deriver().run(stream)

    output_list: list[Deriver.Outputs] = []
    output_sink = TestingSink(output_list)
    op.output("out", transformed_stream, output_sink)

    run_main(flow)

    return (
        DataFrame([output.model_dump(by_alias=True) for output in output_list])
        .set_index("timestamp")
        .tz_convert(df_timezone)
    )
