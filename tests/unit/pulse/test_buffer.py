
import pytest

from forge_base.pulse.basic_collector import ExecutionRecord
from forge_base.pulse.buffer import AsyncBuffer
from forge_base.pulse.exceptions import PulseConfigError


def _record(cid: str = "test") -> ExecutionRecord:
    return ExecutionRecord(
        correlation_id=cid,
        use_case_name="TestUC",
        value_track="legacy",
        subtrack="",
        feature="",
        duration_ms=1.0,
        success=True,
        error_type="",
    )


@pytest.mark.pulse
class TestAsyncBufferValidation:
    def test_max_size_zero_raises(self):
        with pytest.raises(PulseConfigError, match="max_size"):
            AsyncBuffer(max_size=0)

    def test_invalid_policy_raises(self):
        with pytest.raises(PulseConfigError, match="drop_policy"):
            AsyncBuffer(drop_policy="random")


@pytest.mark.pulse
class TestAsyncBufferPush:
    def test_push_returns_true(self):
        buf = AsyncBuffer(max_size=10)
        assert buf.push(_record()) is True

    def test_push_increments_size(self):
        buf = AsyncBuffer(max_size=10)
        buf.push(_record())
        buf.push(_record())
        assert buf.size == 2

    def test_oldest_drop_policy(self):
        buf = AsyncBuffer(max_size=2, drop_policy="oldest")
        buf.push(_record("a"))
        buf.push(_record("b"))
        assert buf.push(_record("c")) is True
        assert buf.size == 2
        assert buf.drop_count == 1

    def test_newest_drop_policy(self):
        buf = AsyncBuffer(max_size=2, drop_policy="newest")
        buf.push(_record("a"))
        buf.push(_record("b"))
        assert buf.push(_record("c")) is False
        assert buf.size == 2
        assert buf.drop_count == 1


@pytest.mark.pulse
class TestAsyncBufferFlush:
    @pytest.mark.asyncio
    async def test_flush_drains_buffer(self):
        buf = AsyncBuffer(max_size=10)
        buf.push(_record("a"))
        buf.push(_record("b"))
        flushed: list[ExecutionRecord] = []
        count = await buf.flush(flushed.append)
        assert count == 2
        assert buf.size == 0
        assert len(flushed) == 2

    @pytest.mark.asyncio
    async def test_flush_empty_buffer(self):
        buf = AsyncBuffer(max_size=10)
        flushed: list[ExecutionRecord] = []
        count = await buf.flush(flushed.append)
        assert count == 0
        assert buf.size == 0

    @pytest.mark.asyncio
    async def test_oldest_drop_preserves_order(self):
        buf = AsyncBuffer(max_size=2, drop_policy="oldest")
        buf.push(_record("a"))
        buf.push(_record("b"))
        buf.push(_record("c"))  # drops "a"
        flushed: list[ExecutionRecord] = []
        await buf.flush(flushed.append)
        assert [r.correlation_id for r in flushed] == ["b", "c"]
