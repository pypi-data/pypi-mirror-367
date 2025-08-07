from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Iso8601DataTime = str
NotionColor = Literal[
    "default",
    "gray",
    "brown",
    "orange",
    "yellow",
    "green",
    "blue",
    "purple",
    "pink",
    "blue_background",
    "brown_background",
    "gray_background",
    "green_background",
    "orange_background",
    "pink_background",
    "purple_background",
    "red",
    "red_background",
    "yellow_background",
]


class RichTextBase(BaseModel):
    class Annotations(BaseModel):
        bold: bool = False
        italic: bool = False
        strikethrough: bool = False
        underline: bool = False
        code: bool = False
        color: NotionColor

    # type: Literal["text", "mention", "equation"]
    annotations: RichTextBase.Annotations
    plain_text: str
    href: str | None = None


class RichTextText(RichTextBase):
    type: Literal["text"]


class RichTextEquation(RichTextBase):
    class Equation(BaseModel):
        expression: str

    type: Literal["equation"]
    equation: Equation


class UserBase(BaseModel):
    object: Literal["user"]
    id: str
    name: str | None = None
    avatar_url: str | None = None


class PeopleUser(UserBase):
    type: Literal["person"] = "person"
    person: Any = None


class BotUser(UserBase):
    type: Literal["bot"] = "bot"
    bot: dict[str, Any] = {}
    owner: dict[str, Any] = {}
    owner_type: Literal["user", "workspace"] = Field(default="workspace", alias="owner.type")
    workspace_name: str | None = None
    workspace_limits: dict[str, Any] = {}
    workspace_limits_max_file_upload_size_in_bytes: int = Field(
        default=0, alias="workspace_limits.max_file_upload_size_in_bytes"
    )


User = PeopleUser | BotUser


class RichTextMention(RichTextBase):
    class Mention(BaseModel):
        type: Literal["user", "page", "database", "date"]
        user: User | None = None
        page: str | None = None
        database: str | None = None
        date: dict[str, Any] | None = None

    type: Literal["mention"]
    mention: Mention


class EmojiObject(BaseModel):
    type: Literal["emoji"]
    emoji: str


class FileObjProps:
    class Notion(BaseModel):
        url: str
        expiry_time: Iso8601DataTime

    class Uploaded(BaseModel):
        id: str

    class External(BaseModel):
        url: str


class NotionHostedFile(BaseModel):
    type: Literal["file"]
    file: FileObjProps.Notion


class UploadedFile(BaseModel):
    type: Literal["file_upload"]
    file_upload: FileObjProps.Uploaded


class ExternalFile(BaseModel):
    type: Literal["external"]
    external: FileObjProps.External


class ParentDatabase(BaseModel):
    type: Literal["database_id"]
    database_id: str


class ParentPage(BaseModel):
    type: Literal["page_id"]
    page_id: str


class ParentWorkspace(BaseModel):
    type: Literal["workspace"]
    workspace: bool = True


class ParentBlock(BaseModel):
    type: Literal["block_id"]
    block_id: str


class PagePropertiesTitle(BaseModel):
    class TitleProperty(BaseModel):
        id: Literal["title"]
        type: Literal["title"]
        title: list[RichTextText]

    title: PagePropertiesTitle.TitleProperty


class PageBase(BaseModel):
    object: Literal["page"]
    id: str
    created_time: Iso8601DataTime
    created_by: User
    last_edited_time: Iso8601DataTime
    last_edited_by: User
    archived: bool
    in_trash: bool
    icon: ExternalFile | UploadedFile | EmojiObject | None
    cover: NotionHostedFile | ExternalFile | UploadedFile | None
    url: str
    public_url: str | None


class PageWithPageParent(PageBase):
    properties: PagePropertiesTitle
    parent: ParentPage | ParentBlock | ParentWorkspace

    def __str__(self) -> str:
        if not self.properties.title.title:
            return f"Page(id={self.id}, title=None)"
        return f"Page(id={self.id}, title={self.properties.title.title[0].plain_text})"


class PageWithDbParent(PageBase):
    properties: Any  # TODO implement PagePropertiesGroup
    parent: ParentDatabase

    def __str__(self) -> str:
        return f"Page(id={self.id} database_page)"


Page = PageWithPageParent | PageWithDbParent

# region: Blocks


class BlockBase(BaseModel):
    object: Literal["block"]
    id: str
    parent: ParentPage | ParentDatabase | ParentBlock
    created_time: Iso8601DataTime
    created_by: User
    last_edited_time: Iso8601DataTime
    last_edited_by: User
    archived: bool
    in_trash: bool
    has_children: bool

    def __str__(self) -> str:
        return f"Block(id={self.id}, has_children={self.has_children}, type={self.type})"  # type: ignore


class BlockParagraph(BlockBase):
    class Paragraph(BaseModel):
        color: NotionColor
        rich_text: list[RichTextBase]
        children: list[NotionBlock] = []

    type: Literal["paragraph"]
    paragraph: Paragraph


class BlockBulletedListItem(BlockBase):
    class BulletedListItem(BaseModel):
        color: NotionColor
        rich_text: list[RichTextBase]
        children: list[BlockBase] = []

    type: Literal["bulleted_list_item"]
    bulleted_list_item: BulletedListItem


class BlockCallout(BlockBase):
    class Callout(BaseModel):
        color: NotionColor
        rich_text: list[RichTextBase]
        icon: ExternalFile | UploadedFile | EmojiObject | None = None

    type: Literal["callout"]
    callout: Callout


class BlockColumnList(BlockBase):
    type: Literal["column_list"]
    column_list: dict[str, Any] = {}


class BlockChildDatabase(BlockBase):
    class ChildDatabase(BaseModel):
        title: str

    type: Literal["child_database"]
    child_database: ChildDatabase


class BlockChildPage(BlockBase):
    class ChildPage(BaseModel):
        title: str

    type: Literal["child_page"]
    child_page: ChildPage


class BlockColumn(BlockBase):
    class Column(BaseModel):
        width_ratio: float

    type: Literal["column"]
    column: Column


class _HeadingProperties(BaseModel):
    rich_text: list[RichTextBase]
    color: NotionColor
    is_toggleable: bool = False


class BlockHeading1(BlockBase):
    type: Literal["heading_1"]
    heading_1: _HeadingProperties


class BlockHeading2(BlockBase):
    type: Literal["heading_2"]
    heading_2: _HeadingProperties


class BlockHeading3(BlockBase):
    type: Literal["heading_3"]
    heading_3: _HeadingProperties


class BlockNumberedListItem(BlockBase):
    class NumberedListItemProperties(BaseModel):
        rich_text: list[RichTextBase]
        color: NotionColor
        children: list[BlockNumberedListItem] = []

    type: Literal["numbered_list_item"]
    numbered_list_item: NumberedListItemProperties


class BlockQuote(BlockBase):
    class QuoteProperties(BaseModel):
        rich_text: list[RichTextBase]
        color: NotionColor
        children: list[BlockQuote] = []

    type: Literal["quote"]
    quote: QuoteProperties


class BlockTable(BlockBase):
    class Table(BaseModel):
        table_width: int
        has_column_header: bool
        has_row_header: bool

    type: Literal["table"]
    table: Table


class BlockTableRow(BlockBase):
    class TableRow(BaseModel):
        cells: list[list[RichTextBase]]

    type: Literal["table_row"]
    table_row: TableRow


class BlockTableOfContents(BlockBase):
    class TableOfContents(BaseModel):
        color: NotionColor

    type: Literal["table_of_contents"]
    table_of_contents: TableOfContents


class BlockTodo(BlockBase):
    class Todo(BaseModel):
        rich_text: list[RichTextBase]
        checked: bool
        color: NotionColor
        children: list[BlockTodo] = []

    type: Literal["to_do"]
    to_do: Todo


class BlockToggle(BlockBase):
    class Toggle(BaseModel):
        rich_text: list[RichTextBase]
        color: NotionColor
        children: list[BlockToggle] = []

    type: Literal["toggle"]
    toggle: Toggle


class BlockBookmark(BlockBase):
    class Bookmark(BaseModel):
        url: str
        caption: list[RichTextBase] = []

    type: Literal["bookmark"]
    bookmark: Bookmark


class BlockBreadcrumb(BlockBase):
    class Breadcrumb(BaseModel):
        items: list[Page]

    type: Literal["breadcrumb"]
    breadcrumb: dict[str, Any] = {}


class BlockCode(BlockBase):
    class Code(BaseModel):
        rich_text: list[RichTextBase]
        caption: list[RichTextBase] = []
        language: Literal[
            "abap",
            "arduino",
            "bash",
            "basic",
            "c",
            "clojure",
            "coffeescript",
            "c++",
            "c#",
            "css",
            "dart",
            "diff",
            "docker",
            "elixir",
            "elm",
            "erlang",
            "flow",
            "fortran",
            "f#",
            "gherkin",
            "glsl",
            "go",
            "graphql",
            "groovy",
            "haskell",
            "html",
            "java",
            "javascript",
            "json",
            "julia",
            "kotlin",
            "latex",
            "less",
            "lisp",
            "livescript",
            "lua",
            "makefile",
            "markdown",
            "markup",
            "matlab",
            "mermaid",
            "nix",
            "objective-c",
            "ocaml",
            "pascal",
            "perl",
            "php",
            "plain text",
            "powershell",
            "prolog",
            "protobuf",
            "python",
            "r",
            "reason",
            "ruby",
            "rust",
            "sass",
            "scala",
            "scheme",
            "scss",
            "shell",
            "sql",
            "swift",
            "typescript",
            "vb.net",
            "verilog",
            "vhdl",
            "visual basic",
            "webassembly",
            "xml",
            "yaml",
            "java/c/c++/c#",
        ]

    type: Literal["code"]
    code: Code


class BlockDivider(BlockBase):
    type: Literal["divider"]
    divider: dict[str, Any] = {}


class BlockEmbed(BlockBase):
    class Embed(BaseModel):
        url: str

    type: Literal["embed"]
    embed: Embed


class BlockEquation(BlockBase):
    class Equation(BaseModel):
        expression: str

    type: Literal["equation"]
    equation: Equation


class BlockFile(BlockBase):
    class FileBase(BaseModel):
        caption: list[RichTextBase]
        name: str

    class NotionFile(FileBase):
        type: Literal["file"]
        file: FileObjProps.Notion

    class ExternalFile(FileBase):
        type: Literal["external"]
        external: FileObjProps.External

    class UploadedFile(FileBase):
        type: Literal["file_upload"]
        file_upload: FileObjProps.Uploaded

    type: Literal["file"]
    file: NotionFile | ExternalFile | UploadedFile


class BlockImage(BlockBase):
    type: Literal["image"]
    image: NotionHostedFile | ExternalFile | UploadedFile


class BlockPdf(BlockBase):
    class PdfBase(BaseModel):
        caption: list[RichTextBase] = []

    class NotionHostedFile(BaseModel):
        type: Literal["file"]
        file: FileObjProps.Notion

    class ExternalFile(BaseModel):
        type: Literal["external"]
        external: FileObjProps.External

    class UploadedFile(BaseModel):
        type: Literal["file_upload"]
        file_upload: FileObjProps.Uploaded

    type: Literal["pdf"]
    pdf: NotionHostedFile | ExternalFile | UploadedFile


NotionBlockWithChildren = (
    BlockParagraph
    | BlockBulletedListItem
    | BlockCallout
    | BlockChildDatabase
    | BlockChildPage
    | BlockColumnList
    | BlockHeading1
    | BlockHeading2
    | BlockHeading3
    | BlockNumberedListItem
    | BlockQuote
    | BlockTable
    | BlockTodo
    | BlockToggle
)

NotionBlock = (
    NotionBlockWithChildren
    | BlockColumn
    | BlockTableRow
    | BlockTableOfContents
    | BlockBookmark
    | BlockBreadcrumb
    | BlockCode
    | BlockDivider
    | BlockEmbed
    | BlockEquation
    | BlockFile
    | BlockImage
    | BlockPdf
)

# endregion: Blocks

# region: Databases


class DatabasePropertiesBase(BaseModel):
    id: str
    name: str
    description: str | None = None


class DatabasePropertiesCheckbox(DatabasePropertiesBase):
    type: Literal["checkbox"]
    checkbox: dict[str, Any] = {}


class DatabasePropertiesCreatedBy(DatabasePropertiesBase):
    type: Literal["created_by"]
    created_by: dict[str, Any] = {}


class DatabasePropertiesCreatedTime(DatabasePropertiesBase):
    type: Literal["created_time"]
    created_time: dict[str, Any] = {}


class DatabasePropertiesDate(DatabasePropertiesBase):
    type: Literal["date"]
    date: dict[str, Any] = {}


class DatabasePropertiesEmail(DatabasePropertiesBase):
    type: Literal["email"]
    email: dict[str, Any] = {}


class DatabasePropertiesFiles(DatabasePropertiesBase):
    type: Literal["files"]
    files: list[NotionHostedFile | ExternalFile | UploadedFile] = []


class DatabasePropertiesFormula(DatabasePropertiesBase):
    class Formula(BaseModel):
        expression: str

    type: Literal["formula"]
    formula: DatabasePropertiesFormula.Formula


class DatabasePropertiesLastEditedBy(DatabasePropertiesBase):
    type: Literal["last_edited_by"]
    last_edited_by: dict[str, Any] = {}


class DatabasePropertiesLastEditedTime(DatabasePropertiesBase):
    type: Literal["last_edited_time"]
    last_edited_time: dict[str, Any] = {}


SelectableColor = Literal[
    "blue",
    "brown",
    "default",
    "gray",
    "green",
    "orange",
    "pink",
    "purple",
    "red",
    "yellow",
]


class DatabasePropertiesMultiSelect(DatabasePropertiesBase):
    class Option(BaseModel):
        id: str
        name: str
        color: SelectableColor

    class MultiSelect(BaseModel):
        options: list[DatabasePropertiesMultiSelect.Option]

    type: Literal["multi_select"]
    multi_select: DatabasePropertiesMultiSelect.MultiSelect


class DatabasePropertiesNumber(DatabasePropertiesBase):
    class Number(BaseModel):
        format: Literal[
            "number",
            "number_with_commas",
            "percent",
            "dollar",
            "euro",
            "pound",
            "yen",
            "won",
            "argentine_peso",
            "baht",
            "australian_dollar",
            "canadian_dollar",
            "chilean_peso",
            "colombian_peso",
            "danish_krone",
            "dirham",
            "forint",
            "franc",
            "hong_kong_dollar",
            "koruna",
            "krona",
            "leu",
            "lira",
            "mexican_peso",
            "new_taiwan_dollar",
            "new_zealand_dollar",
            "norwegian_krone",
            "philippine_peso",
            "peruvian_sol",
            "rand",
            "real",
            "ringgit",
            "riyal",
            "ruble",
            "rupee",
            "rupiah",
            "shekel",
            "singapore_dollar",
            "uruguayan_peso",
            "yuan",
            "zloty",
        ]

    type: Literal["number"]
    number: DatabasePropertiesNumber.Number


class DatabasePropertiesPeople(DatabasePropertiesBase):
    type: Literal["people"]
    people: dict[str, Any] = {}


class DatabasePropertiesPhoneNumber(DatabasePropertiesBase):
    type: Literal["phone_number"]
    phone_number: dict[str, Any] = {}


class DatabasePropertiesRelation(DatabasePropertiesBase):
    class DualProperty(BaseModel):
        synced_property_name: str
        synced_property_id: str

    class Relation(BaseModel):
        database_id: str
        dual_property: DatabasePropertiesRelation.DualProperty

    type: Literal["relation"]
    relation: DatabasePropertiesRelation.Relation


class DatabasePropertiesRichText(DatabasePropertiesBase):
    type: Literal["rich_text"]
    rich_text: dict[str, Any] = {}


class DatabasePropertiesRollup(DatabasePropertiesBase):
    class Rollup(BaseModel):
        function: Literal[
            "average",
            "checked",
            "count_per_group",
            "count",
            "count_values",
            "date_range",
            "earliest_date",
            "empty",
            "latest_date",
            "max",
            "median",
            "min",
            "not_empty",
            "percent_checked",
            "percent_empty",
            "percent_not_empty",
            "percent_per_group",
            "percent_unchecked",
            "range",
            "unchecked",
            "unique",
            "show_original",
            "show_unique",
            "sum",
        ]
        relation_property_id: str
        relation_property_name: str
        rollup_property_id: str
        rollup_property_name: str

    type: Literal["rollup"]
    rollup: DatabasePropertiesRollup.Rollup


class DatabasePropertiesSelect(DatabasePropertiesBase):
    class Option(BaseModel):
        id: str
        name: str
        color: SelectableColor

    class Select(BaseModel):
        options: list[DatabasePropertiesSelect.Option]

    type: Literal["select"]
    select: DatabasePropertiesSelect.Select


class DatabasePropertiesStatus(DatabasePropertiesBase):
    class Option(BaseModel):
        id: str
        name: str
        color: SelectableColor
        description: str | None

    class Group(BaseModel):
        id: str
        name: str
        color: SelectableColor
        option_ids: list[str]

    class Status(BaseModel):
        options: list[DatabasePropertiesStatus.Option]
        groups: list[DatabasePropertiesStatus.Group]

    type: Literal["status"]
    status: DatabasePropertiesStatus.Status


class DatabasePropertiesTitle(DatabasePropertiesBase):
    type: Literal["title"]
    title: dict[str, Any] = {}


class DatabasePropertiesUrl(DatabasePropertiesBase):
    type: Literal["url"]
    url: dict[str, Any] = {}


DatabaseProperties = (
    DatabasePropertiesCheckbox
    | DatabasePropertiesCreatedBy
    | DatabasePropertiesCreatedTime
    | DatabasePropertiesDate
    | DatabasePropertiesEmail
    | DatabasePropertiesFiles
    | DatabasePropertiesFormula
    | DatabasePropertiesLastEditedBy
    | DatabasePropertiesLastEditedTime
    | DatabasePropertiesMultiSelect
    | DatabasePropertiesNumber
    | DatabasePropertiesPeople
    | DatabasePropertiesPhoneNumber
    | DatabasePropertiesRelation
    | DatabasePropertiesRichText
    | DatabasePropertiesRollup
    | DatabasePropertiesSelect
    | DatabasePropertiesStatus
    | DatabasePropertiesTitle
    | DatabasePropertiesUrl
)


class Database(BaseModel):
    object: Literal["database"]
    id: str
    created_time: Iso8601DataTime
    created_by: User
    last_edited_time: Iso8601DataTime
    last_edited_by: User
    title: list[RichTextText]
    description: list[RichTextBase]
    icon: NotionHostedFile | ExternalFile | UploadedFile | EmojiObject | None
    cover: NotionHostedFile | ExternalFile | UploadedFile | None
    properties: dict[str, DatabaseProperties]
    parent: ParentPage | ParentBlock | ParentWorkspace
    url: str
    archived: bool
    in_trash: bool
    is_inline: bool = False
    public_utl: str | None = None


# endregion: Databases


class Comment(BaseModel):
    class Attachment(BaseModel):
        file_upload_id: str
        type: Literal["file_upload"] | None = None

    class DisplayName(BaseModel):
        type: Literal["integration", "user", "custom"]
        custom: dict[str, Any]

    object: Literal["comment"]
    id: str
    parent: ParentPage | ParentBlock
    discussion_id: str
    created_time: Iso8601DataTime
    last_edited_time: Iso8601DataTime
    created_by: User
    rich_text: list[RichTextBase]
    attachments: list[Attachment]
    display_name: DisplayName


class FileUpload(BaseModel):
    object: Literal["file_upload"]
    id: str
    created_time: Iso8601DataTime
    last_edited_time: Iso8601DataTime
    expiry_time: str | None
    status: Literal["pending", "uploaded", "expired", "failed"]
    filename: str | None
    content_type: str | None
    content_length: int | None
    upload_url: str | None = None
    complete_url: str | None = None
    file_import_result: str | None = None
