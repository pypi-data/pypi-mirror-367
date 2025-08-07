from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat, NonNegativeInt


class WithFadeTimeData(BaseModel):
    fade_time: Optional[NonNegativeFloat] = Field(None, alias="fadeTime")


class DimmableWithFadeData(WithFadeTimeData):
    dim_value: float = Field(alias="dimValue", ge=0.0, le=100.0)


class SceneWithFadeData(WithFadeTimeData):
    scene: int = Field(ge=0, lt=16)


class ColorRGBData(BaseModel):
    """Data model for the ``colorRGB`` feature."""

    red: Optional[float] = Field(
        None,
        description="Relative red value in the [0, 1] interval.",
        alias="r",
        ge=0.0,
        le=1.0,
    )
    green: Optional[float] = Field(
        None,
        description="Relative green value in the [0, 1] interval.",
        alias="g",
        ge=0.0,
        le=1.0,
    )
    blue: Optional[float] = Field(
        None,
        description="Relative blue value in the [0, 1] interval.",
        alias="b",
        ge=0.0,
        le=1.0,
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"r": 0.0, "g": 0.5, "b": 1.0}]}
    )


class DimmableRGBData(ColorRGBData):
    dimmable: float = Field(
        50.0,
        description="Percentage in the [0, 100] interval to dim a device to.",
        ge=0.0,
        le=100.0,
    )


class ColorRGBWithFadeData(WithFadeTimeData):
    color: ColorRGBData


class ColorWAFData(BaseModel):
    """Data model for the ``colorWAF`` feature."""

    white: Optional[float] = Field(
        None,
        description="Relative white value in the [0, 1] interval.",
        alias="w",
        ge=0.0,
        le=1.0,
    )
    amber: Optional[float] = Field(
        None,
        description="Relative amber value in the [0, 1] interval.",
        alias="a",
        ge=0.0,
        le=1.0,
    )
    free_color: Optional[float] = Field(
        None,
        description="Relative free color value in the [0, 1] interval.",
        alias="f",
        ge=0.0,
        le=1.0,
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"w": 0.0, "a": 0.5, "f": 1.0}]}
    )


class DimmableWAFData(ColorWAFData):
    dimmable: float = Field(
        50.0,
        description="Percentage in the [0, 100] interval to dim a device to.",
        ge=0.0,
        le=100.0,
    )


class ColorWAFWithFadeData(WithFadeTimeData):
    color: ColorWAFData


class DimmableKelvinData(BaseModel):
    dimmable: float = Field(
        50.0,
        description="Percentage in the [0, 100] interval to dim a device to.",
        ge=0.0,
        le=100.0,
    )
    kelvin: NonNegativeFloat = Field(4000.0, description="Color temperature in Kelvin.")


class ColorKelvinWithFadeData(WithFadeTimeData):
    color: NonNegativeFloat


class ColorXYData(BaseModel):
    """Data model for the ``colorXY`` feature."""

    x: Optional[float] = Field(
        None,
        description="X coordinate in the CIE color chromaticity space.",
    )
    y: Optional[float] = Field(
        None,
        description="Y coordinate in the CIE color chromaticity space.",
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"x": 0.432, "y": 0.150}]}
    )


class DimmableXYData(ColorXYData):
    dimmable: float = Field(
        50.0,
        description="Percentage in the [0, 100] interval to dim a device to.",
        ge=0.0,
        le=100.0,
    )


class ColorXYWithFadeData(WithFadeTimeData):
    color: ColorXYData


class ControlData(BaseModel):
    switchable: Optional[bool] = None
    dimmable: Optional[float] = Field(None, ge=0.0, le=100.0)
    dimmable_with_fade: Optional[DimmableWithFadeData] = Field(
        None, alias="dimmableWithFade"
    )
    dim_up: Optional[int] = Field(None, alias="dimUp", ge=1, le=1)
    dim_down: Optional[int] = Field(None, alias="dimDown", ge=1, le=1)
    goto_last_active: Optional[bool] = Field(
        None,
        description="Value must be ``true``.",
        alias="gotoLastActive",
    )
    goto_last_active_with_fade: Optional[WithFadeTimeData] = Field(
        None,
        description="Dim to the last level within a fade time in seconds.",
        alias="gotoLastActiveWithFade",
    )
    scene: Optional[int] = Field(
        None,
        description="Scene number of the scene to recall.",
        ge=0,
        lt=16,
    )
    scene_with_fade: Optional[SceneWithFadeData] = Field(
        None,
        description="Scene number of the scene to recall, within a fade time in seconds.",
        alias="sceneWithFade",
    )
    fade_time: Optional[NonNegativeFloat] = Field(
        None,
        description="Set the fade time in seconds.",
        alias="fadeTime",
    )
    fade_rate: Optional[NonNegativeFloat] = Field(
        None,
        description="Set the fade rate in steps per second.",
        alias="fadeRate",
    )
    save_to_scene: Optional[NonNegativeInt] = Field(
        None, alias="saveToScene", ge=0, lt=16
    )
    color_rgb: Optional[ColorRGBData] = Field(None, alias="colorRGB")
    dimmable_rgb: Optional[DimmableRGBData] = Field(None, alias="dimmableRGB")
    color_rgb_with_fade: Optional[ColorRGBWithFadeData] = Field(
        None, alias="colorRGBWithFade"
    )
    color_waf: Optional[ColorWAFData] = Field(None, alias="colorWAF")
    dimmable_waf: Optional[DimmableWAFData] = Field(None, alias="dimmableWAF")
    color_waf_with_fade: Optional[ColorWAFWithFadeData] = Field(
        None, alias="colorWAFWithFade"
    )
    color_kelvin: Optional[NonNegativeInt] = Field(
        None, alias="colorKelvin", gt=15, le=1000000
    )
    dimmable_kelvin: Optional[DimmableKelvinData] = Field(None, alias="dimmableKelvin")
    color_kelvin_with_fade: Optional[ColorKelvinWithFadeData] = Field(
        None, alias="colorKelvinWithFade"
    )
    color_xy: Optional[ColorXYData] = Field(None, alias="colorXY")
    dimmable_xy: Optional[DimmableXYData] = Field(None, alias="dimmableXY")
    color_xy_with_fade: Optional[ColorXYWithFadeData] = Field(
        None, alias="colorXYWithFade"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "gotoLastActive": True,
                    "gotoLastActiveWithFade": WithFadeTimeData(fadeTime=1.0),
                    "scene": 15,
                    "sceneWithFade": SceneWithFadeData(scene=15, fadeTime=1.0),
                    "fadeTime": 1.0,
                    "fadeRate": 15.8,
                }
            ]
        }
    )
