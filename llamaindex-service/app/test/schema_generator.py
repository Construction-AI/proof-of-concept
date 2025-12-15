from app.api.services.schema_generator_service import SchemaGeneratorService
from app.models.schema import (
    SchemaMeta,
    SchemaSection,
    SchemaSubsection,
    SchemaSubSubsection,
    SchemaParagraph,
    SchemaBulletList,
    SchemaNumberedList,
    SchemaFieldExtractionField
)
import datetime
import json


def run_test():
    now = datetime.datetime.now().isoformat()
    meta = SchemaMeta(
        company_id="company",
        project_id="project_id",
        author="Jakub Nenczak",
        version_id="1.0.0",
        date_created=now,
        date_modified=now,
        document_type="bioz",
        system_instruction="test",
    )

    generator = SchemaGeneratorService(meta=meta)

    # 2) Section with subsections and subsubsections
    complex_section = SchemaSection(
        name="Complex Section",
        description="A section that demonstrates nested structure.",
        new_page=True,
        subsections=[],
    )

    # Subsection A
    subsection_a = SchemaSubsection(
        name="Subsection A",
        description="Contains paragraphs and a bullet list.",
        subsubsections=[],
    )

    subsub_a1 = SchemaSubSubsection(
        name="SubSub A1",
        description="A mix of paragraph and list elements.",
        elements=[
            SchemaParagraph(text="This is a paragraph element inside SubSub A1."),
            SchemaBulletList(
                elements=[
                    SchemaParagraph(text="Bullet item 1"),
                    SchemaParagraph(text="Bullet item 2"),
                    SchemaParagraph(text="Bullet item 3"),
                ]
            ),
        ],
    )

    subsub_a2 = SchemaSubSubsection(
        name="SubSub A2",
        description="A numbered list example.",
        elements=[
            SchemaNumberedList(
                elements=[
                    SchemaParagraph(text="Step 1: Prepare materials."),
                    SchemaParagraph(text="Step 2: Verify safety conditions."),
                    SchemaParagraph(text="Step 3: Execute procedure."),
                ]
            )
        ],
    )

    subsection_a.subsubsections.extend([subsub_a1, subsub_a2])

    # Subsection B
    subsection_b = SchemaSubsection(
        name="Subsection B",
        description="Demonstrates field extraction element.",
        subsubsections=[],
    )

    subsub_b1 = SchemaSubSubsection(
        name="SubSub B1",
        description="Field extraction example with a prompt.",
        elements=[
            SchemaFieldExtractionField(
                prompt="Extract the main hazard described in the introduction section.",
                type="string",
                example="Exposure to high voltage equipment",
            ),
            SchemaParagraph(text="Additional context or fallback notes."),
        ],
    )

    subsection_b.subsubsections.append(subsub_b1)

    complex_section.subsections.extend([subsection_a, subsection_b])
    generator.sections.append(complex_section)

    # 3) Minimal section with description only
    minimal_section = SchemaSection(
        name="Minimal",
        description="A minimal section without subsections.",
    )
    generator.sections.append(minimal_section)
    
    # Write to file
    with open("/app/generated_schema.json", "w", encoding="utf-8") as f:
        json.dump(generator.serialize(), f, ensure_ascii=False, indent=2)

    print("Generated schema to /app/generated_schema.json")


if __name__ == "__main__":
    run_test()