from types import MappingProxyType

import pytest

from forge_base.pulse.meta import _PULSE_META_ATTR, PulseMeta, pulse_meta, read_pulse_meta


@pytest.mark.pulse
class TestPulseMeta:
    def test_frozen(self):
        m = PulseMeta()
        with pytest.raises(AttributeError):
            m.subtrack = "x"

    def test_defaults(self):
        m = PulseMeta()
        assert m.subtrack == ""
        assert m.feature == ""
        assert m.value_track == ""
        assert m.tags == MappingProxyType({})

    def test_custom_values(self):
        m = PulseMeta(subtrack="checkout", feature="pay", value_track="revenue")
        assert m.subtrack == "checkout"
        assert m.feature == "pay"
        assert m.value_track == "revenue"

    def test_tags_immutable(self):
        m = PulseMeta(tags=MappingProxyType({"env": "prod"}))
        with pytest.raises(TypeError):
            m.tags["new"] = "val"

    def test_empty_tags_singleton(self):
        a = PulseMeta()
        b = PulseMeta()
        assert a.tags is b.tags


@pytest.mark.pulse
class TestPulseMetaDecorator:
    def test_stamps_attribute(self):
        @pulse_meta(subtrack="checkout")
        class MyUseCase:
            pass

        assert hasattr(MyUseCase, _PULSE_META_ATTR)
        meta = getattr(MyUseCase, _PULSE_META_ATTR)
        assert isinstance(meta, PulseMeta)
        assert meta.subtrack == "checkout"

    def test_full_annotation(self):
        @pulse_meta(subtrack="checkout", feature="pay", value_track="revenue")
        class MyUseCase:
            pass

        meta = getattr(MyUseCase, _PULSE_META_ATTR)
        assert meta.subtrack == "checkout"
        assert meta.feature == "pay"
        assert meta.value_track == "revenue"

    def test_partial_annotation_leaves_defaults(self):
        @pulse_meta(subtrack="checkout")
        class MyUseCase:
            pass

        meta = getattr(MyUseCase, _PULSE_META_ATTR)
        assert meta.subtrack == "checkout"
        assert meta.feature == ""
        assert meta.value_track == ""

    def test_empty_annotation(self):
        @pulse_meta()
        class MyUseCase:
            pass

        meta = getattr(MyUseCase, _PULSE_META_ATTR)
        assert meta.subtrack == ""
        assert meta.feature == ""
        assert meta.value_track == ""

    def test_returns_same_class(self):
        class Original:
            pass

        decorated = pulse_meta(subtrack="x")(Original)
        assert decorated is Original

    def test_tags_dict_to_mapping_proxy(self):
        @pulse_meta(tags={"env": "prod", "tier": "premium"})
        class MyUseCase:
            pass

        meta = getattr(MyUseCase, _PULSE_META_ATTR)
        assert isinstance(meta.tags, MappingProxyType)
        assert meta.tags == MappingProxyType({"env": "prod", "tier": "premium"})

    def test_tags_none_gives_empty(self):
        @pulse_meta(tags=None)
        class MyUseCase:
            pass

        meta = getattr(MyUseCase, _PULSE_META_ATTR)
        assert meta.tags == MappingProxyType({})

    def test_tags_empty_dict_gives_empty(self):
        @pulse_meta(tags={})
        class MyUseCase:
            pass

        meta = getattr(MyUseCase, _PULSE_META_ATTR)
        assert meta.tags == MappingProxyType({})


@pytest.mark.pulse
class TestReadPulseMeta:
    def test_reads_from_instance(self):
        @pulse_meta(subtrack="checkout")
        class MyUseCase:
            pass

        instance = MyUseCase()
        meta = read_pulse_meta(instance)
        assert meta is not None
        assert meta.subtrack == "checkout"

    def test_none_for_undecorated(self):
        class PlainUseCase:
            pass

        assert read_pulse_meta(PlainUseCase()) is None

    def test_inheritance_reads_parent(self):
        @pulse_meta(subtrack="parent_sub")
        class Base:
            pass

        class Child(Base):
            pass

        meta = read_pulse_meta(Child())
        assert meta is not None
        assert meta.subtrack == "parent_sub"

    def test_subclass_override(self):
        @pulse_meta(subtrack="parent_sub")
        class Base:
            pass

        @pulse_meta(subtrack="child_sub")
        class Child(Base):
            pass

        assert read_pulse_meta(Base()).subtrack == "parent_sub"
        assert read_pulse_meta(Child()).subtrack == "child_sub"

    def test_arbitrary_object(self):
        assert read_pulse_meta("a string") is None
        assert read_pulse_meta(42) is None
        assert read_pulse_meta(None) is None
