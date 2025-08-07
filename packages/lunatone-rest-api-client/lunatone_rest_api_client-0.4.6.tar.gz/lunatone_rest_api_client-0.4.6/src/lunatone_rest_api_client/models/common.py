from enum import IntEnum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, NonNegativeInt


StatusT = TypeVar("StatusT")
ColorT = TypeVar("ColorT")


class Status(BaseModel, Generic[StatusT]):
    status: StatusT


class FadeTime(BaseModel):
    fade_time: float = Field(alias="fadeTime")


class DimmableWithFade(BaseModel):
    dim_value: float = Field(alias="dimValue")
    fade_time: float = Field(alias="fadeTime")


class ColorWithFadeTime(BaseModel, Generic[ColorT]):
    color: ColorT
    fade_time: float = Field(alias="fadeTime")


class ColorRGB(BaseModel):
    red: float = Field(alias="r")
    green: float = Field(alias="g")
    blue: float = Field(alias="b")
    dimmable: Optional[float] = None


class ColorWAF(BaseModel):
    white: float = Field(alias="w")
    amber: float = Field(alias="a")
    free_color: float = Field(alias="f")
    dimmable: Optional[float] = None


class ColorKelvinDimmable(BaseModel):
    dimmable: Optional[float] = None
    kelvin: NonNegativeInt


class ColorXY(BaseModel):
    x: float
    y: float
    dimmable: Optional[float] = None


class TimeSignature(BaseModel):
    timestamp: float
    counter: int


class FeaturesStatus(BaseModel):
    switchable: Optional[Status[bool]] = None
    dimmable: Optional[Status[float]] = None
    dimmable_with_fade: Optional[Status[DimmableWithFade]] = Field(
        None, alias="dimmableWithFade"
    )
    dim_up: Optional[bool] = Field(None, alias="dimUp")
    dim_down: Optional[bool] = Field(None, alias="dimDown")
    scene: Optional[bool] = None
    scene_with_fade: Optional[Status[FadeTime]] = Field(None, alias="sceneWithFade")
    goto_last_active: Optional[dict] = Field(None, alias="gotoLastActive")
    goto_last_active_with_fade: Optional[Status[FadeTime]] = Field(
        None, alias="gotoLastActiveWithFade"
    )
    dali_cmd16: Optional[bool] = Field(None, alias="daliCmd16")
    fade_time: Optional[Status[float]] = Field(None, alias="fadeTime")
    fade_rate: Optional[Status[float]] = Field(None, alias="fadeRate")
    save_to_scene: Optional[bool] = Field(None, alias="saveToScene")
    color_rgb: Optional[Status[ColorRGB]] = Field(None, alias="colorRGB")
    dimmable_rgb: Optional[Status[ColorRGB]] = Field(None, alias="dimmableRGB")
    color_rgb_with_fade: Optional[Status[ColorWithFadeTime[ColorRGB]]] = Field(
        None, alias="colorRGBWithFade"
    )
    color_waf: Optional[Status[ColorWAF]] = Field(None, alias="colorWAF")
    dimmable_waf: Optional[Status[ColorWAF]] = Field(None, alias="dimmableWAF")
    color_waf_with_fade: Optional[Status[ColorWithFadeTime[ColorWAF]]] = Field(
        None, alias="colorWAFWithFade"
    )
    color_kelvin: Optional[Status[NonNegativeInt]] = Field(None, alias="colorKelvin")
    dimmable_kelvin: Optional[Status[ColorKelvinDimmable]] = Field(
        None, alias="dimmableKelvin"
    )
    color_kelvin_with_fade: Optional[Status[ColorWithFadeTime[NonNegativeInt]]] = Field(
        None, alias="colorKelvinWithFade"
    )
    color_xy: Optional[Status[ColorXY]] = Field(None, alias="colorXY")
    dimmable_xy: Optional[Status[ColorXY]] = Field(None, alias="dimmableXY")
    color_xy_with_fade: Optional[Status[ColorWithFadeTime[ColorXY | dict]]] = Field(
        None, alias="colorXYWithFade"
    )


class DALIType(IntEnum):
    DT0_FLUORESCENT_LAMPS = 0
    DT1_EMERGENCY_LIGHTING = 1
    DT2_DISCHARGE_LAMPS = 2
    DT3_LOW_VOLTAGE_HALOGEN_LAMPS = 3
    DT4_SUPPLY_VOLTAGE_CONTROLLER = 4
    DT5_CONVERSION_FROM_DIGITAL_SIGNAL_INTO_DC_VOLTAGE = 5
    DT6_LED_MODULES = 6
    DT7_SWITCHING_FUNCTION = 7
    DT8_COLOUR_CONTROL = 8
    DT9_SEQUENCER = 9
