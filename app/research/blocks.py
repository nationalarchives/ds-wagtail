from wagtail import blocks


class SearchCodeBlock(blocks.StructBlock):
	code = blocks.CharBlock(
		label="Code",
		help_text="The catalogue code to add to the user's search, for example MAF 37.",
	)
	definition = blocks.CharBlock(
		label="Definition",
		help_text="A plain-English explanation of the code, for example Farm survey maps.",
	)


class FixedSearchFilterBlock(blocks.StructBlock):
	parameter = blocks.ChoiceBlock(
		label="Search parameter",
		choices=[
			("q", "Search query"),
			("covering_date_from-year", "Record date from: year"),
			("covering_date_from-month", "Record date from: month"),
			("covering_date_from-day", "Record date from: day"),
			("covering_date_to-year", "Record date to: year"),
			("covering_date_to-month", "Record date to: month"),
			("covering_date_to-day", "Record date to: day"),
			("opening_date_from-year", "Record opening date from: year"),
			("opening_date_from-month", "Record opening date from: month"),
			("opening_date_from-day", "Record opening date from: day"),
			("opening_date_to-year", "Record opening date to: year"),
			("opening_date_to-month", "Record opening date to: month"),
			("opening_date_to-day", "Record opening date to: day"),
			("level", "Level"),
			("collection", "Collection"),
			("subject", "Subject"),
		],
		help_text="The query-string parameter that will be fixed for this search.",
	)
	value = blocks.CharBlock(
		label="Value",
		help_text="The value to send for this parameter.",
	)
	explanation = blocks.CharBlock(
		label="Plain-English explanation",
		required=False,
		help_text="Optional explanation shown alongside this fixed filter.",
	)


class GuidedSearchBlock(blocks.StructBlock):
	codes = blocks.ListBlock(
		SearchCodeBlock(),
		required=False,
		label="Code options",
		help_text="Codes users can choose to add to their search.",
	)
	free_text_search = blocks.BooleanBlock(
		required=False,
		default=True,
		label="Allow free-text search",
		help_text="Allows users to add search terms using the q query parameter.",
	)
	search_help_text = blocks.CharBlock(
		required=False,
		label="Free-text search guidance",
		help_text="Optional guidance for the user's free-text search.",
	)
	available_filters = blocks.ListBlock(
		blocks.ChoiceBlock(
			choices=[
				("covering_date", "Record date"),
				("opening_date", "Record opening date"),
				("level", "Level"),
				("collection", "Collections"),
				("subject", "Subjects"),
			]
		),
		required=False,
		label="Available filters",
		help_text="Filters users can set. Date filters support an optional date range.",
	)
	fixed_filters = blocks.ListBlock(
		FixedSearchFilterBlock(),
		required=False,
		label="Fixed filters",
		help_text="Filters that are always applied to this search, with an optional plain-English explanation.",
	)

	class Meta:
		label = "Guided search"
