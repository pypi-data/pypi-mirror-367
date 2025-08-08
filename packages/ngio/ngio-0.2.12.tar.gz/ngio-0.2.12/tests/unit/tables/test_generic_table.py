from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from anndata import AnnData

from ngio.tables.tables_container import open_table, write_table
from ngio.tables.v1 import GenericTable


@pytest.mark.parametrize("backend", ["experimental_json_v1", "anndata_v1"])
def test_generic_df_table(tmp_path: Path, backend: str):
    store = tmp_path / "test.zarr"
    test_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    table = GenericTable(dataframe=test_df)
    assert isinstance(table.__repr__(), str)

    write_table(store=store, table=table, backend=backend)

    loaded_table = open_table(store=store)
    assert isinstance(loaded_table, GenericTable)
    assert set(loaded_table.dataframe.columns) == {"a", "b"}
    for column in loaded_table.dataframe.columns:
        pd.testing.assert_series_equal(
            loaded_table.dataframe[column], test_df[column], check_index=False
        )


@pytest.mark.parametrize("backend", ["anndata_v1"])
def test_generic_anndata_table(tmp_path: Path, backend: str):
    store = tmp_path / "test.zarr"
    test_df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    test_obs = pd.DataFrame({"c": ["a", "b", "c"]})
    test_obs.index = test_obs.index.astype(str)
    test_obsm = np.random.normal(0, 1, size=(3, 2))

    anndata = AnnData(X=test_df, obs=test_obs)
    anndata.obsm["test"] = test_obsm

    table = GenericTable(anndata=anndata)

    table.dataframe = test_df
    assert not table.anndata_native
    table.anndata = anndata
    assert table.anndata_native

    write_table(store=store, table=table, backend=backend)

    loaded_table = open_table(store=store)
    assert isinstance(loaded_table, GenericTable)

    loaded_ad = loaded_table.anndata
    loaded_df = loaded_table.dataframe
    assert set(loaded_df.columns) == {"a", "b", "c"}

    np.testing.assert_allclose(loaded_ad.obsm["test"], test_obsm)  # type: ignore
