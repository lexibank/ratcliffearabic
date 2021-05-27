from collections import defaultdict

import attr
from pathlib import Path
from pylexibank import Concept, Language, FormSpec
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar

from clldutils.misc import slug


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    NameInSource = attr.ib(default=None)
    NameInCognates = attr.ib(default=None)


class Dataset(BaseDataset):
    id = "ratcliffearabic"
    dir = Path(__file__).parent
    concept_class = CustomConcept
    language_class = CustomLanguage

    form_spec = FormSpec(separators=",;/", first_form_only=True, replacements=[
        ("  ", "_"), (" ", "_")])

    def cmd_makecldf(self, args):
        languages = args.writer.add_languages(lookup_factory="NameInSource")
        languagesc = {}
        for language in self.languages:
            languagesc[language["NameInCognates"]] = language["ID"]

        args.writer.add_sources()
        concepts = {}
        for concept in self.concepts:
            idx = concept['NUMBER']+'_'+slug(concept['ENGLISH'])
            args.writer.add_concept(
                    ID=idx,
                    Name=concept['ENGLISH'],
                    Number=concept['NUMBER'],
                    #Concepticon_ID=concept['CONCEPTICON_ID'],
                    #Concepticon_Gloss=concept['CONCEPTICON_GLOSS']
                    )
            concepts[concept['ENGLISH']] = idx
            concepts[concept['LEXIBANK_GLOSS']] = idx

        data = self.raw_dir.read_csv("wordlist.tsv", delimiter="\t", dicts=True)
        cogs = self.raw_dir.read_csv("cognates.tsv", delimiter="\t",
                dicts=True)
        for row, cogsets in progressbar(zip(data, cogs)):
            if row["Number"].isdigit():
                for language, lid in languages.items():
                    value = row[language]
                    if not value.isdigit():
                        lex = args.writer.add_forms_from_value(
                                Parameter_ID=concepts[row["Concept"]],
                                Language_ID=lid,
                                Value=value,
                                Source=''
                                )
                        #args.writer.add_cognate(
                        #        lexeme=lex,
                        #        Cognateset_ID=cognacy,
                        #        Source=''
                        #        )

