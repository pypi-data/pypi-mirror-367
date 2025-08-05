"""Ramifice - Field of Model for enter phone number."""

__all__ = ("PhoneField",)

import logging

import phonenumbers

from ramifice.fields.general.field import Field
from ramifice.fields.general.text_group import TextGroup
from ramifice.utils import constants
from ramifice.utils.mixins.json_converter import JsonMixin

logger = logging.getLogger(__name__)


class PhoneField(Field, TextGroup, JsonMixin):
    """Ramifice - Field of Model for enter phone number.

    WARNING: By default is used validator `phonenumbers.is_valid_number()`.
    """

    def __init__(  # noqa: D107
        self,
        label: str = "",
        disabled: bool = False,
        hide: bool = False,
        ignored: bool = False,
        hint: str = "",
        warning: list[str] | None = None,
        default: str | None = None,
        placeholder: str = "",
        required: bool = False,
        readonly: bool = False,
        unique: bool = False,
    ):
        if constants.DEBUG:
            try:
                if default is not None:
                    if not isinstance(default, str):
                        raise AssertionError("Parameter `default` - Not а `str` type!")
                    if len(default) == 0:
                        raise AssertionError(
                            "The `default` parameter should not contain an empty string!"
                        )
                    try:
                        phone_default = phonenumbers.parse(default)
                        if not phonenumbers.is_valid_number(phone_default):
                            raise AssertionError()
                    except phonenumbers.phonenumberutil.NumberParseException:
                        raise AssertionError("Parameter `default` - Invalid Phone number!")
                if not isinstance(label, str):
                    raise AssertionError("Parameter `default` - Not а `str` type!")
                if not isinstance(disabled, bool):
                    raise AssertionError("Parameter `disabled` - Not а `bool` type!")
                if not isinstance(hide, bool):
                    raise AssertionError("Parameter `hide` - Not а `bool` type!")
                if not isinstance(ignored, bool):
                    raise AssertionError("Parameter `ignored` - Not а `bool` type!")
                if not isinstance(ignored, bool):
                    raise AssertionError("Parameter `ignored` - Not а `bool` type!")
                if not isinstance(hint, str):
                    raise AssertionError("Parameter `hint` - Not а `str` type!")
                if warning is not None and not isinstance(warning, list):
                    raise AssertionError("Parameter `warning` - Not а `list` type!")
                if not isinstance(placeholder, str):
                    raise AssertionError("Parameter `placeholder` - Not а `str` type!")
                if not isinstance(required, bool):
                    raise AssertionError("Parameter `required` - Not а `bool` type!")
                if not isinstance(readonly, bool):
                    raise AssertionError("Parameter `readonly` - Not а `bool` type!")
                if not isinstance(unique, bool):
                    raise AssertionError("Parameter `unique` - Not а `bool` type!")
            except AssertionError as err:
                logger.critical(str(err))
                raise err

        Field.__init__(
            self,
            label=label,
            disabled=disabled,
            hide=hide,
            ignored=ignored,
            hint=hint,
            warning=warning,
            field_type="PhoneField",
            group="text",
        )
        TextGroup.__init__(
            self,
            input_type="tel",
            placeholder=placeholder,
            required=required,
            readonly=readonly,
            unique=unique,
        )
        JsonMixin.__init__(self)

        self.default = default
