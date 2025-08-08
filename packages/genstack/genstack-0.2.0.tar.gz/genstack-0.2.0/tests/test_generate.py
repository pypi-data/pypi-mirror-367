from genstack import Genstack
import pytest

def test_generate_with_invalid_type():
    client = Genstack(api_key="gen-")
    with pytest.raises(TypeError):
        client.generate(input=123, track="test-track")