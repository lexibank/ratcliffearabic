from pathlib import Path

import attr
from clldutils.misc import slug
from pylexibank import Concept, Language, FormSpec
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    NameInSource = attr.ib(default=None)
    NameInCognates = attr.ib(default=None)
    Sources = attr.ib(default=None)


class Dataset(BaseDataset):
    id = "ratcliffearabic"
    dir = Path(__file__).parent
    concept_class = CustomConcept
    language_class = CustomLanguage

    form_spec = FormSpec(
        separators=",;/", first_form_only=True, replacements=[("  ", "_"), (" ", "_")]
    )

    def cmd_makecldf(self, args):
        languages = args.writer.add_languages(lookup_factory="NameInSource")
        languagesc, sources = {}, {}

        for language in self.languages:
            languagesc[language["NameInSource"]] = language["NameInCognates"]
            sources[language["NameInSource"]] = language["Sources"].split(",")
        args.writer.add_sources()

        concepts = args.writer.add_concepts(
            id_factory=lambda x: x.id.split("-")[-1] + "_" + slug(x.english),
            lookup_factory=lambda concept: "".join(concept.attributes["lexibank_gloss"]),
        )

        data = self.raw_dir.read_csv("wordlist.tsv", delimiter="\t", dicts=True)
        cogs = self.raw_dir.read_csv("cognates.tsv", delimiter="\t", dicts=True)
        for row, cogsets in progressbar(zip(data, cogs)):
            if row["Number"].isdigit():
                for language, lid in languages.items():
                    value = row[language]
                    if not value.isdigit():
                        lex = args.writer.add_forms_from_value(
                            Parameter_ID=concepts[row["Concept"]],
                            Language_ID=lid,
                            Value=value,
                            Source=sources[language],
                        )
                        if lex:
                            if cogsets[languagesc[language]] == "1":
                                args.writer.add_cognate(
                                    lexeme=lex[0],
                                    Cognateset_ID=slug(row["Concept"]),
                                    Source="Ratcliffe2021",
                                )
