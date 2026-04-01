from html import escape

from wagtail import blocks


class CodeBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(
        label="Code language",
        required=False,
        choices=[
            ("html", "HTML"),
            ("javascript", "JavaScript"),
            ("python", "Python"),
            ("xml", "XML"),
            ("json", "JSON"),
            ("bash", "Bash"),
            ("git", "git"),
            ("markdown", "Markdown"),
            ("graphql", "GraphQL"),
            ("powershell", "PowerShell"),
            ("yaml", "YAML"),
        ],
    )
    code = blocks.TextBlock(max_length=500)
    filename = blocks.CharBlock(
        label="Code block title",
        required=False,
        help_text="Display a filename with the extension e.g. example.html",
        max_length=100,
    )
    allow_copying = blocks.BooleanBlock(
        default=False, help_text="Allow copy to clipboard"
    )

    def get_api_representation(self, value, context=None):
        representation = {
            "code": escape(value["code"]),
            "allow_copying": value["allow_copying"],
        }
        if value["language"]:
            representation["language"] = value["language"]
        if value["filename"]:
            representation["filename"] = value["filename"]

        return representation

    class Meta:
        icon = "code"
        label = "Code"
