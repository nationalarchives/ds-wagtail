from html import escape

from wagtail import blocks


class CodeBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(
        label="Language choice",
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
    code = blocks.TextBlock(help_text="Add raw (unescaped) code here")
    filename = blocks.CharBlock(
        required=False, help_text="Include file extension e.g. filename.html"
    )
    allow_copying = blocks.BooleanBlock(
        default=False, help_text="Allow copy to clipboard"
    )

    def get_api_representation(self, value, context=None):
        return {
            "language": value.language,
            "code": value.code,
            "html_escaped_code": escape(value.code),
        }

    class Meta:
        icon = "code"
        label = "Code"
