class BuildError(Exception):
    """Fehler waehrend des Build-Prozesses."""


class ValidationError(Exception):
    """Fehlerhafte Benutzereingaben."""


class ConfigurationError(Exception):
    """Ungueltige Konfiguration."""
