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
        heading=SchemaParagraph(text="Complex Section"),
        description=SchemaParagraph(text="A section that demonstrates nested structure."),
        new_page=True,
        subsections=[],
    )

    # Subsection A
    subsection_a = SchemaSubsection(
        heading=SchemaParagraph(text="Subsection A"),
        description=SchemaParagraph(text="Contains paragraphs and a bullet list."),
        subsubsections=[],
    )

    subsub_a1 = SchemaSubSubsection(
        heading=SchemaParagraph(text="SubSub A1"),
        description=SchemaParagraph(text="A mix of paragraph and list elements."),
        elements=[
            SchemaParagraph(text="This is a paragraph element inside SubSub A1."),
            SchemaBulletList(
                heading=SchemaParagraph(text="Tralala"),
                elements=[
                    SchemaParagraph(text="Bullet item 1"),
                    SchemaParagraph(text="Bullet item 2"),
                    SchemaParagraph(text="Bullet item 3"),
                ]
            ),
        ],
    )

    subsub_a2 = SchemaSubSubsection(
        heading=SchemaParagraph(text="SubSub A2"),
        description=SchemaParagraph(text="A numbered list example."),
        elements=[
            SchemaNumberedList(
                heading=SchemaParagraph(text="Tralala"),
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
        heading=SchemaParagraph(text="Subsection B"),
        description=SchemaParagraph(text="Demonstrates field extraction element."),
        subsubsections=[],
    )

    subsub_b1 = SchemaSubSubsection(
        heading=SchemaParagraph(text="SubSub B1"),
        description=SchemaParagraph(text="Field extraction example with a prompt."),
        elements=[
            SchemaFieldExtractionField(
                prompt="Extract the main hazard described in the introduction section.",
                data_type="string",
                example="Exposure to high voltage equipment",
            ),
            SchemaFieldExtractionField(
                prompt="Extract all safety measures mentioned in the document.",
                data_type="list",
                example=["Personal protective equipment (PPE)", "Emergency procedures", "First aid kit location"],
            ),
            SchemaFieldExtractionField(
                prompt="Extract the responsible personnel heading and role.",
                data_type="string",
                example="John Smith, Safety Officer",
            ),
            SchemaParagraph(text="Additional context or fallback notes."),
        ],
    )

    subsection_b.subsubsections.append(subsub_b1)

    complex_section.subsections.extend([subsection_a, subsection_b])
    generator.sections.append(complex_section)

    # 3) Minimal section with description only
    minimal_section = SchemaSection(
        heading=SchemaParagraph(text="Minimal"),
        description=SchemaParagraph(text="A minimal section without subsections."),
    )
    generator.sections.append(minimal_section)
    
    # Write to file
    with open("/app/generated_schema.json", "w", encoding="utf-8") as f:
        json.dump(generator.serialize(), f, ensure_ascii=False, indent=2)

    print("Generated schema to /app/generated_schema.json")
    
    # DocxGenerator
    from app.api.services.docx_generator_service import DocxGeneratorService
    docx_generator = DocxGeneratorService(
        schema_generator_service=generator
    )
    
    docx_generator.load_schema()
    docx_generator.generate()


if __name__ == "__main__":
    run_test()