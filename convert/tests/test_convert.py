import os
from io import BytesIO
from pathlib import Path

from pytest_mock import MockerFixture
from rio_cogeo.cogeo import cog_validate

from convert.cog import to_cog


def test_to_cog(test_dir: str, tmp_path: Path, mocker: MockerFixture):
    image_path = os.path.join(test_dir, "data", "landsat.tif")
    out_path = str(tmp_path / "cog.tif")

    # Mock the read/write of the S3 Helper so it does not actually hit S3
    def mock_get_bytes(self, key):
        with open(image_path, "rb") as fh:
            buf = BytesIO(fh.read())
        return buf

    def mock_write_bytes(self, content, key):
        with open(out_path, "wb") as fh:
            fh.write(content.getbuffer())

    mocker.patch(
        "convert.s3.S3Helper.get_bytes",
        mock_get_bytes,
    )

    mocker.patch(
        "convert.s3.S3Helper.write_bytes",
        mock_write_bytes,
    )

    # Mocking the call to S3 so the input/output keys do not matter
    to_cog("asd", "asd", "asd", "asd")

    # ensure we created a valid COG with no errors or warnings
    assert os.path.exists(out_path)

    is_valid, errors, warnings = cog_validate(out_path)
    assert is_valid
    assert not errors
    assert not warnings
