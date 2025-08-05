from __future__ import annotations

import re
import math
from datetime import datetime, timedelta
from typing import ClassVar, Self

from ..exceptions import InvalidTargetTime, ValidationError


class Duration:
    """
    🇧🇷 Classe para manipulação de durações em minutos com parsing flexível de strings.

    🇺🇸 Class for handling durations in minutes with flexible string parsing.
    """

    _time_pattern: ClassVar[re.Pattern] = re.compile(r"(\d+)([smhd]?)", re.IGNORECASE)

    def __init__(self, minutes: float = 0.0) -> None:
        """
        🇧🇷 Inicializa uma duração.

        📋 Parâmetros:
        - minutes (float): Duração inicial em minutos (padrão 0.0)

        ⚠️ Exceções:
        - ValidationError: Se o valor for negativo

        🇺🇸 Initializes a duration.

        📋 Parameters:
        - minutes (float): Initial duration in minutes (default 0.0)

        ⚠️ Raises:
        - ValidationError: If the value is negative
        """
        if minutes < 0:
            raise ValidationError("Duration must be non-negative")
        self._minutes = minutes

    def _parse(self, value: str) -> float:
        """
        🇧🇷 Converte string para minutos. Aceita formatos como "5", "1h30m", "2d5h", "45s".

        📋 Parâmetros:
        - value (str): Duração textual

        📤 Retorna:
        - float: duração em minutos

        ⚠️ Exceções:
        - ValidationError: Formato inválido

        🇺🇸 Converts a string to minutes. Supports formats like "5", "1h30m", "2d5h", "45s".

        📋 Parameters:
        - value (str): Duration text

        📤 Returns:
        - float: duration in minutes

        ⚠️ Raises:
        - ValidationError: Invalid format
        """
        matches = self._time_pattern.findall(value.strip().lower())
        if not matches:
            raise ValidationError(f"Invalid duration format: '{value}'")

        total = 0.0
        for amount_str, unit in matches:
            amount = int(amount_str)
            match unit:
                case "s":
                    total += amount / 60
                case "m" | "":
                    total += amount
                case "h":
                    total += amount * 60
                case "d":
                    total += amount * 1440
                case _:
                    raise ValidationError(f"Invalid duration unit: '{unit}'")
        return total

    def _apply(self, value: int | float | str, subtract: bool = False) -> Self:
        delta = (
            float(value)
            if isinstance(value, (int, float))
            else self._parse(value)
            if isinstance(value, str)
            else None
        )

        if delta is None:
            raise ValidationError(f"Invalid type for duration: {type(value)}")

        self._minutes += -delta if subtract else delta

        if self._minutes < 0:
            raise ValidationError("Resulting duration must be non-negative")

        return self

    def until(self, target_time: str) -> Duration:
        """
        🇧🇷 Retorna a duração até um horário futuro no formato "HH:MM".

        📋 Parâmetros:
        - target_time (str): Horário alvo no formato "HH:MM"

        📤 Retorna:
        - Duration: Duração até o horário alvo

        ⚠️ Exceções:
        - InvalidTargetTime: Se o horário for inválido ou já tiver passado

        🇺🇸 Returns the duration until a future time in "HH:MM" format.

        📋 Parameters:
        - target_time (str): Target time as "HH:MM"

        📤 Returns:
        - Duration: Duration until the target time

        ⚠️ Raises:
        - InvalidTargetTime: If the time is invalid or already passed
        """
        try:
            now = datetime.now().replace(second=0, microsecond=0)
            target = datetime.strptime(target_time, "%H:%M").replace(
                year=now.year, month=now.month, day=now.day
            )
        except ValueError as e:
            raise InvalidTargetTime(f"Invalid format for target time: {target_time!r}") from e

        if target < now:
            raise InvalidTargetTime(f"Target time {target_time!r} is in the past.")

        return Duration((target - now).total_seconds() / 60)

    def add(self, value: int | float | str) -> Self:
        """🇧🇷 Adiciona um valor à duração. | 🇺🇸 Adds a value to the duration."""
        return self._apply(value)

    def sub(self, value: int | float | str) -> Self:
        """🇧🇷 Subtrai um valor da duração. | 🇺🇸 Subtracts a value from the duration."""
        return self._apply(value, subtract=True)

    def minutes(self) -> int:
        """🇧🇷 Retorna a duração em minutos, arredondada para cima. | 🇺🇸 Returns duration in minutes, rounded up."""
        return math.ceil(self._minutes)

    def seconds(self) -> float:
        """🇧🇷 Retorna a duração em segundos. | 🇺🇸 Returns the duration in seconds."""
        return self._minutes * 60

    def ms(self) -> float:
        """🇧🇷 Retorna a duração em milissegundos. | 🇺🇸 Returns the duration in milliseconds."""
        return self.seconds() * 1000

    def timestamp(self) -> int:
        """
        🇧🇷 Retorna o timestamp futuro com base na duração atual.

        🇺🇸 Returns the future timestamp based on the current duration.
        """
        return int((datetime.now() + timedelta(minutes=self._minutes)).timestamp())

    def __repr__(self) -> str:
        return f"<Duration: {self._minutes:.2f} min>"
