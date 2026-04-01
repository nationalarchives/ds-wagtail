from html import escape

from wagtail import blocks


class CodeBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(
        label="Code language",
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
        return {
            "language": value["language"],
            "code": escape(value["code"]),
            "filename": value["filename"],
            "allow_copying": value["allow_copying"],
        }

    class Meta:
        icon = "code"
        label = "Code"
