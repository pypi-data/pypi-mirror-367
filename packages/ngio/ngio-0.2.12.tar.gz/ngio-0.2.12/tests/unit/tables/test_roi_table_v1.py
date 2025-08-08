from pathlib import Path

import pandas as pd
import pytest

from ngio.tables import RoiTable
from ngio.tables.backends._anndata_v1 import AnnDataBackend
from ngio.tables.tables_container import open_table, write_table
from ngio.tables.v1._roi_table import Roi, RoiTableV1, RoiTableV1Meta
from ngio.utils import NgioValueError, ZarrGroupHandler


def test_roi_table_v1(tmp_path: Path):
    rois = {
        "roi1": Roi(
            name="roi1",
            x=0.0,
            y=0.0,
            z=0.0,
            x_length=1.0,
            y_length=1.0,
            z_length=1.0,
            unit="micrometer",  # type: ignore
        )
    }

    table = RoiTableV1(rois=rois.values())
    assert isinstance(table.__repr__(), str)

    table.add(
        roi=Roi(
            name="roi2",
            x=0.0,
            y=0.0,
            z=0.0,
            x_length=1.0,
            y_length=1.0,
            z_length=1.0,
            unit="micrometer",  # type: ignore
        )
    )

    with pytest.raises(NgioValueError):
        # ROI name already exists
        table.add(
            roi=Roi(
                name="roi2",
                x=0.0,
                y=0.0,
                z=0.0,
                x_length=1.0,
                y_length=1.0,
                z_length=1.0,
                unit="micrometer",  # type: ignore
            )
        )

    table.add(
        roi=Roi(
            name="roi2",
            x=0.0,
            y=0.0,
            z=0.0,
            x_length=1.0,
            y_length=1.0,
            z_length=1.0,
            unit="micrometer",  # type: ignore
        ),
        overwrite=True,
    )

    write_table(store=tmp_path / "roi_table.zarr", table=table, backend="anndata_v1")

    loaded_table = open_table(store=tmp_path / "roi_table.zarr")
    assert isinstance(loaded_table, RoiTableV1)

    assert len(loaded_table._rois) == 2
    assert loaded_table.get("roi1") == table.get("roi1")
    assert loaded_table.get("roi2") == table.get("roi2")

    with pytest.raises(NgioValueError):
        loaded_table.get("roi3")

    assert loaded_table._meta.backend == "anndata_v1"
    assert loaded_table._meta.fractal_table_version == loaded_table.version()
    assert loaded_table._meta.type == loaded_table.type()


def test_roi_no_index(tmp_path: Path):
    """ngio needs to support reading a table without an index. for legacy reasons"""
    handler = ZarrGroupHandler(tmp_path / "roi_table.zarr")
    backend = AnnDataBackend(
        group_handler=handler,
    )

    roi_table = pd.DataFrame(
        {
            "x_micrometer": [0.0, 1.0],
            "y_micrometer": [0.0, 1.0],
            "z_micrometer": [0.0, 1.0],
            "len_x_micrometer": [1.0, 1.0],
            "len_y_micrometer": [1.0, 1.0],
            "len_z_micrometer": [1.0, 1.0],
        }
    )
    roi_table.index = pd.Index(["roi_1", "roi_2"])

    backend.write(
        roi_table,
        metadata=RoiTableV1Meta().model_dump(exclude_none=True),
    )

    roi_table = RoiTable._from_handler(handler=handler)
    assert isinstance(roi_table, RoiTable)
    assert len(roi_table.rois()) == 2
