"""Button platform."""

from __future__ import annotations

from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SimpleIrrigationCoordinator
from .entity import SimpleIrrigationEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up buttons."""
    coordinator: SimpleIrrigationCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    runtime = hass.data[DOMAIN][entry.entry_id]["runtime"]
    entities: list[ButtonEntity] = [
        RunDueButton(coordinator, runtime),
        StopAllButton(coordinator, runtime),
    ]
    for zid, zone in coordinator.installation.zones.items():
        entities.append(ZoneRunButton(coordinator, runtime, zid, zone.name))
    async_add_entities(entities)

    known = set(coordinator.installation.zones)

    @callback
    def _sync_zone_buttons() -> None:
        new_entities: list[ButtonEntity] = []
        for zid, zone in coordinator.installation.zones.items():
            if zid in known:
                continue
            known.add(zid)
            new_entities.append(ZoneRunButton(coordinator, runtime, zid, zone.name))
        if new_entities:
            async_add_entities(new_entities)

    entry.async_on_unload(coordinator.async_add_listener(_sync_zone_buttons))


class RunDueButton(SimpleIrrigationEntity, ButtonEntity):
    """Run zones due now (same window as service)."""

    _attr_translation_key = "run_due"

    def __init__(self, coordinator: SimpleIrrigationCoordinator, runtime: Any) -> None:
        """Initialize."""
        super().__init__(coordinator, "button_run_due")
        self._runtime = runtime

    async def async_press(self) -> None:
        """Run due."""
        await self._runtime.async_run_due_now()


class StopAllButton(SimpleIrrigationEntity, ButtonEntity):
    """Stop all."""

    _attr_translation_key = "stop_all"

    def __init__(self, coordinator: SimpleIrrigationCoordinator, runtime: Any) -> None:
        """Initialize."""
        super().__init__(coordinator, "button_stop_all")
        self._runtime = runtime

    async def async_press(self) -> None:
        """Stop."""
        await self._runtime.async_stop_all()


class ZoneRunButton(SimpleIrrigationEntity, ButtonEntity):
    """Manual zone run."""

    def __init__(
        self,
        coordinator: SimpleIrrigationCoordinator,
        runtime: Any,
        zone_id: str,
        zone_name: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, f"zone_{zone_id}_run")
        self._runtime = runtime
        self._zone_id = zone_id
        self._attr_translation_key = "zone_run_now"
        self._attr_translation_placeholders = {"zone_name": zone_name}

    @property
    def available(self) -> bool:
        """A deleted zone's old entity must not remain actionable."""
        return super().available and self._zone_id in self.coordinator.installation.zones

    async def async_press(self) -> None:
        """Run zone."""
        await self._runtime.async_run_zone(self._zone_id, duration_min=None)

