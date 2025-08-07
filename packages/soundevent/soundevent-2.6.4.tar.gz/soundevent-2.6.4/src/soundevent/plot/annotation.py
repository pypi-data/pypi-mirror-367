"""Functions for plotting annotations."""

from typing import Iterable, Optional

from matplotlib.axes import Axes

from soundevent import data
from soundevent.geometry.operations import Positions, get_geometry_point
from soundevent.plot.common import create_axes
from soundevent.plot.geometries import plot_geometry
from soundevent.plot.tags import TagColorMapper, add_tags_legend, plot_tag

__all__ = [
    "plot_annotation",
    "plot_annotations",
]


def plot_annotation(
    annotation: data.SoundEventAnnotation,
    ax: Optional[Axes] = None,
    position: Positions = "top-right",
    color_mapper: Optional[TagColorMapper] = None,
    time_offset: float = 0.001,
    freq_offset: float = 1000,
    color: Optional[str] = None,
    **kwargs,
) -> Axes:
    """Plot an annotation."""
    geometry = annotation.sound_event.geometry

    if geometry is None:
        raise ValueError("Annotation does not have a geometry.")

    if ax is None:
        ax = create_axes(**kwargs)

    if color_mapper is None:
        color_mapper = TagColorMapper()

    ax = plot_geometry(geometry, ax=ax, color=color, **kwargs)

    x, y = get_geometry_point(geometry, position=position)

    for index, tag in enumerate(annotation.tags):
        color = color_mapper.get_color(tag)
        ax = plot_tag(
            time=x + time_offset,
            frequency=y - index * freq_offset,
            color=color,
            ax=ax,
            **kwargs,
        )

    return ax


def plot_annotations(
    annotations: Iterable[data.SoundEventAnnotation],
    ax: Optional[Axes] = None,
    position: Positions = "top-right",
    color_mapper: Optional[TagColorMapper] = None,
    time_offset: float = 0.001,
    freq_offset: float = 1000,
    legend: bool = True,
    color: Optional[str] = None,
    **kwargs,
):
    """Plot an annotation."""
    if ax is None:
        ax = create_axes(**kwargs)

    if color_mapper is None:
        color_mapper = TagColorMapper()

    for annotation in annotations:
        ax = plot_annotation(
            annotation,
            ax=ax,
            position=position,
            color_mapper=color_mapper,
            time_offset=time_offset,
            freq_offset=freq_offset,
            color=color,
            **kwargs,
        )

    if legend:
        ax = add_tags_legend(ax, color_mapper)

    return ax
