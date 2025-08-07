import re


def _get_body(func):
    import inspect
    import re

    source_lines = inspect.getsource(func).splitlines()
    first_line = source_lines[0]
    if not re.match(r"def \w+\((\w+(, \w+)*)?\):", first_line.strip()):
        # Parsing to AST and unparsing is a more robust option,
        # but more complicated.
        raise Exception(f"def and parameters should fit on one line: {first_line}")

    # The "def" should not be in the output,
    # and cleandoc handles the first line differently.
    source_lines[0] = ""
    body = inspect.cleandoc("\n".join(source_lines))
    body = re.sub(
        r"\s*#\s+type:\s+ignore\s*",
        "\n",
        body,
    )
    body = re.sub(
        r"\s*#\s+noqa:.+",
        "",
        body,
    )
    return body


class Template:
    def __init__(self, template, root=None):
        if root is not None:
            template_name = f"_{template}.py"
            template_path = root / template_name
            self._source = f"'{template_name}'"
            self._template = template_path.read_text()
        else:
            if callable(template):
                self._source = "function template"
                self._template = _get_body(template)
            else:
                self._source = "string template"
                self._template = template
        # We want a list of the initial slots, because substitutions
        # can produce sequences of upper case letters that could be mistaken for slots.
        self._initial_slots = self._find_slots()

    def _find_slots(self):
        # Slots:
        # - are all caps or underscores
        # - have word boundary on either side
        # - are at least three characters
        slot_re = r"\b[A-Z][A-Z_]{2,}\b"
        return set(re.findall(slot_re, self._template))

    def fill_expressions(self, **kwargs):
        """
        Fill in variable names, or dicts or lists represented as strings.
        """
        for k, v in kwargs.items():
            k_re = re.escape(k)
            self._template, count = re.subn(rf"\b{k_re}\b", str(v), self._template)
            if count == 0:
                raise Exception(
                    f"No '{k}' slot to fill with '{v}' in "
                    f"{self._source}:\n\n{self._template}"
                )
        return self

    def fill_values(self, **kwargs):
        """
        Fill in string or numeric values. `repr` is called before filling.
        """
        for k, v in kwargs.items():
            k_re = re.escape(k)
            self._template, count = re.subn(rf"\b{k_re}\b", repr(v), self._template)
            if count == 0:
                raise Exception(
                    f"No '{k}' slot to fill with '{v}' in "
                    f"{self._source}:\n\n{self._template}"
                )
        return self

    def fill_blocks(self, **kwargs):
        """
        Fill in code blocks. Slot must be alone on line.
        """
        for k, v in kwargs.items():
            if not isinstance(v, str):
                raise Exception(f"For {k} in {self._source}, expected string, not {v}")

            def match_indent(match):
                # This does what we want, but binding is confusing.
                return "\n".join(
                    match.group(1) + line for line in v.split("\n")  # noqa: B023
                )

            k_re = re.escape(k)
            self._template, count = re.subn(
                rf"^([ \t]*){k_re}$",
                match_indent,
                self._template,
                flags=re.MULTILINE,
            )
            if count == 0:
                base_message = (
                    f"No '{k}' slot to fill with '{v}' in "
                    f"{self._source}:\n\n{self._template}"
                )
                if k in self._template:
                    raise Exception(
                        f"Block slots must be alone on line; {base_message}"
                    )
                raise Exception(base_message)
        return self

    def finish(self) -> str:
        unfilled_slots = self._initial_slots & self._find_slots()
        if unfilled_slots:
            slots_str = ", ".join(sorted(f"'{slot}'" for slot in unfilled_slots))
            raise Exception(
                f"{slots_str} slot not filled "
                f"in {self._source}:\n\n{self._template}"
            )
        return self._template
